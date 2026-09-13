# BUILD PROMPT 2 of 5 — generator.py

Build `generator.py`. This module runs all 120 generations (2 models × 4 strategies × 3 tasks × 5 test cases) and saves raw output. Import all data from `config.py` — do not redefine models, strategies, or tasks here.

## Requirements:

**1. API clients**
- OpenAI: use the `openai` Python SDK, key from `os.environ["OPENAI_API_KEY"]` (load via `python-dotenv`)
- Llama 3 via Groq: use the `groq` Python SDK, key from `os.environ["GROQ_API_KEY"]`
- Write one function per provider: `call_openai(prompt: str) -> str` and `call_groq(prompt: str) -> str`, both returning just the text response

**2. Retry logic**
Wrap both API call functions with retry logic: max 3 attempts, exponential backoff (e.g. 2s, 4s, 8s) on failure. Use a decorator or the `tenacity` library. On final failure after 3 attempts, log the error and store `"ERROR"` as the response rather than crashing the whole run.

**3. Main generation loop**
Nested loop structure:
```
for task_name, task_data in TASKS.items():
    for strategy_name, strategy_fn in STRATEGIES.items():
        for model_name, model_info in MODELS.items():
            for i, test_input in enumerate(task_data["test_cases"]):
                prompt = strategy_fn(task_data["instruction"], test_input)
                response = call_openai(prompt) if model_info["provider"] == "openai" else call_groq(prompt)
                # store row
```

**4. Row schema — append each result as a row with these exact columns:**
```
task_category, strategy, model_name, test_case_index, input_text, prompt_used, response_text, timestamp
```

**5. Progress logging**
Print one line per generation in this format:
```
[{count}/120] {model_name} | {strategy_name} | {task_category} | test_case_{i}
```

**6. Output**
Save all 120 rows to `config.RAW_RESPONSES_PATH` as CSV using pandas. Create the `data/` directory if it doesn't exist. If the script is re-run, it should overwrite the file cleanly (don't append to a stale file).

**7. Small delay**
Add a `time.sleep(0.5)` between calls to avoid rate-limit issues — adjust if the user's API tier allows faster calls.

Confirm the script runs end-to-end and produces a 120-row CSV with the exact schema above, then stop and wait for Build Prompt 3.
