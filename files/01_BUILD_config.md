# BUILD PROMPT 1 of 5 — config.py

Build `config.py`. This file holds ONLY static data and constants — no API calls, no logic. Every other module will import from this file.

## Required contents:

**1. Model registry**
```python
MODELS = {
    "gpt-4o-mini": {"provider": "openai", "model_id": "gpt-4o-mini"},
    "llama3-70b": {"provider": "groq", "model_id": "llama3-70b-8192"}
}
```

**2. Prompt strategy templates**
Define all 4 strategies as Python functions that take `(task_instruction, input_text)` and return a fully-formed prompt string:
- `zero_shot(task_instruction, input_text)` — direct instruction + input, no examples
- `few_shot(task_instruction, input_text)` — instruction + 2-3 hardcoded worked examples relevant to that task category + input
- `chain_of_thought(task_instruction, input_text)` — instruction + "Let's think step by step" scaffold + input
- `role_based(task_instruction, input_text)` — instruction wrapped in an expert persona (e.g. "You are an expert linguist/analyst..." tailored per task) + input

Store these in a dict:
```python
STRATEGIES = {
    "zero_shot": zero_shot,
    "few_shot": few_shot,
    "chain_of_thought": chain_of_thought,
    "role_based": role_based
}
```

**3. Task categories and test cases**
Define 3 task categories, each with a task instruction and exactly 5 fixed test inputs:
```python
TASKS = {
    "classification": {
        "instruction": "Classify the sentiment of the following text as Positive, Negative, or Neutral.",
        "test_cases": [ "...", "...", "...", "...", "..." ]  # 5 short real text snippets
    },
    "summarization": {
        "instruction": "Summarize the following passage in 2-3 sentences.",
        "test_cases": [ "...", "...", "...", "...", "..." ]  # 5 short passages (3-5 sentences each)
    },
    "reasoning": {
        "instruction": "Solve the following problem, showing your reasoning.",
        "test_cases": [ "...", "...", "...", "...", "..." ]  # 5 logic/math word problems of varying difficulty
    }
}
```
Populate these with real, varied, non-trivial content — not placeholders. Classification examples should have genuinely mixed sentiment (not all obviously positive). Reasoning problems should require actual multi-step logic (not one-line arithmetic).

**4. Judge rubric constants**
```python
RUBRIC_WEIGHTS = {
    "accuracy": 0.4,
    "relevance": 0.2,
    "coherence": 0.2,
    "completeness": 0.2
}
```

**5. Paths**
```python
DATA_DIR = "data"
RAW_RESPONSES_PATH = "data/raw_responses.csv"
SCORED_RESPONSES_PATH = "data/scored_responses.csv"
SUMMARY_PATH = "data/summary_by_group.csv"
FINDINGS_PATH = "findings.md"
```

Do not write generator/judge/aggregator logic in this file. Confirm the file is complete and syntactically valid, then stop and wait for Build Prompt 2.
