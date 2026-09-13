import os
import time
import datetime
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

import config

load_dotenv()

groq_key = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=groq_key) if groq_key else None

def return_error(retry_state):
    print(f"\n[Error] Failed after {retry_state.attempt_number} attempts: {retry_state.outcome.exception()}")
    return "ERROR"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=8),
    retry_error_callback=return_error
)
def call_groq(prompt: str, model_id: str) -> str:
    response = groq_client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content

def main():
    if not groq_key:
        print("Warning: Missing API key. Make sure GROQ_API_KEY is set in .env")
        
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    rows = []
    total_generations = len(config.TASKS) * len(config.STRATEGIES) * len(config.MODELS) * 5
    count = 1
    
    for task_name, task_data in config.TASKS.items():
        for strategy_name, strategy_fn in config.STRATEGIES.items():
            for model_name, model_info in config.MODELS.items():
                for i, test_input in enumerate(task_data["test_cases"]):
                    print(f"[{count}/{total_generations}] {model_name} | {strategy_name} | {task_name} | test_case_{i}")
                    
                    prompt = strategy_fn(task_data["instruction"], test_input)
                    
                    if model_info["provider"] == "groq":
                        response_text = call_groq(prompt, model_info["model_id"]) if groq_key else "ERROR"
                    else:
                        response_text = "ERROR: Unknown provider"
                    
                    timestamp = datetime.datetime.now().isoformat()
                    
                    rows.append({
                        "task_category": task_name,
                        "strategy": strategy_name,
                        "model_name": model_name,
                        "test_case_index": i,
                        "input_text": test_input,
                        "prompt_used": prompt,
                        "response_text": response_text,
                        "timestamp": timestamp
                    })
                    
                    count += 1
                    time.sleep(0.5)
    
    df = pd.DataFrame(rows)
    df.to_csv(config.RAW_RESPONSES_PATH, index=False)
    print(f"\nDone! Saved {len(df)} rows to {config.RAW_RESPONSES_PATH}")

if __name__ == "__main__":
    main()
