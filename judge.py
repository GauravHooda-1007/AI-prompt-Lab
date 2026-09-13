import os
import json
import time
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

import config

load_dotenv()

groq_key = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=groq_key) if groq_key else None

def return_error(retry_state):
    print(f"\n[Error] API call failed after {retry_state.attempt_number} attempts: {retry_state.outcome.exception()}")
    return None

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=8),
    retry_error_callback=return_error
)
def call_judge_api(prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content

def parse_judge_response(response_text: str):
    clean_text = response_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    return json.loads(clean_text.strip())

def main():
    if not groq_key:
        print("Warning: Missing GROQ_API_KEY in .env. Judging will return None for all scores.")
    
    if not os.path.exists(config.RAW_RESPONSES_PATH):
        print(f"Error: {config.RAW_RESPONSES_PATH} not found. Run generator.py first.")
        return

    df = pd.read_csv(config.RAW_RESPONSES_PATH)
    total_rows = len(df)
    
    scored_rows = []
    
    for idx, row in df.iterrows():
        count = idx + 1
        model_name = row['model_name']
        strategy_name = row['strategy']
        task_category = row['task_category']
        test_case_idx = row['test_case_index']
        
        print(f"[{count}/{total_rows}] Judging: {model_name} | {strategy_name} | {task_category} | test_case_{test_case_idx}")
        
        task_instruction = config.TASKS[task_category]["instruction"]
        input_text = row['input_text']
        response_text = row['response_text']
        
        if pd.isna(response_text) or response_text == "ERROR":
            parsed = None
        else:
            base_prompt = f"""You are an impartial evaluator. Score the following AI response on a scale of 1-5 for each criterion.

TASK INSTRUCTION: {task_instruction}
INPUT: {input_text}
AI RESPONSE: {response_text}

Score on:
1. accuracy (1-5): factual/logical correctness
2. relevance (1-5): does it address what was asked
3. coherence (1-5): clarity and structure
4. completeness (1-5): does it fully answer

Respond with ONLY valid JSON, no other text, no markdown fences:
{{"accuracy": <int>, "relevance": <int>, "coherence": <int>, "completeness": <int>, "justification": "<one sentence>"}}"""
            
            judge_response = call_judge_api(base_prompt) if groq_client else None
            parsed = None
            
            if judge_response:
                try:
                    parsed = parse_judge_response(judge_response)
                except Exception:
                    strict_prompt = base_prompt + "\n\nCRITICAL: Return ONLY the JSON object, nothing else. No markdown, no intro."
                    judge_response = call_judge_api(strict_prompt) if groq_client else None
                    if judge_response:
                        try:
                            parsed = parse_judge_response(judge_response)
                        except Exception as e:
                            print(f"  [Parse Error] Failed twice to parse JSON: {e}")
                            parsed = None

        row_dict = row.to_dict()
        if parsed:
            try:
                acc = float(parsed['accuracy'])
                rel = float(parsed['relevance'])
                coh = float(parsed['coherence'])
                cmp = float(parsed['completeness'])
                just = parsed.get('justification', '')
                
                comp_score = (
                    config.RUBRIC_WEIGHTS["accuracy"] * acc +
                    config.RUBRIC_WEIGHTS["relevance"] * rel +
                    config.RUBRIC_WEIGHTS["coherence"] * coh +
                    config.RUBRIC_WEIGHTS["completeness"] * cmp
                )
                
                row_dict.update({
                    "accuracy": acc,
                    "relevance": rel,
                    "coherence": coh,
                    "completeness": cmp,
                    "composite_score": comp_score,
                    "justification": just
                })
            except (KeyError, ValueError, TypeError) as e:
                print(f"  [Data Error] Invalid JSON schema: {e}")
                row_dict.update({
                    "accuracy": None, "relevance": None, "coherence": None,
                    "completeness": None, "composite_score": None, "justification": None
                })
        else:
            row_dict.update({
                "accuracy": None, "relevance": None, "coherence": None,
                "completeness": None, "composite_score": None, "justification": None
            })
            
        scored_rows.append(row_dict)
        time.sleep(0.5)  # Let's adjust to 0.5 to be safe with Groq limits
        
    scored_df = pd.DataFrame(scored_rows)
    scored_df.to_csv(config.SCORED_RESPONSES_PATH, index=False)
    print(f"\nDone! Saved {len(scored_df)} scored rows to {config.SCORED_RESPONSES_PATH}")

if __name__ == "__main__":
    main()
