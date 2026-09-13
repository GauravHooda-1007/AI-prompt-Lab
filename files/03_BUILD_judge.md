# BUILD PROMPT 3 of 5 — judge.py

Build `judge.py`. This module reads `data/raw_responses.csv` (produced by generator.py), scores every row using an LLM judge, and writes `data/scored_responses.csv`. Import weights and paths from `config.py`.

## Requirements:

**1. Judge model**
Use a separate model call from the two being benchmarked to reduce self-preference bias — recommend `gpt-4o-mini` with a dedicated judge system prompt (reuse the `call_openai` function from generator.py, or duplicate a minimal version here — your choice, but avoid circular imports).

**2. Judge prompt template**
Construct a strict-JSON-only prompt per row:
```
You are an impartial evaluator. Score the following AI response on a scale of 1-5 for each criterion.

TASK INSTRUCTION: {task_instruction}
INPUT: {input_text}
AI RESPONSE: {response_text}

Score on:
1. accuracy (1-5): factual/logical correctness
2. relevance (1-5): does it address what was asked
3. coherence (1-5): clarity and structure
4. completeness (1-5): does it fully answer

Respond with ONLY valid JSON, no other text, no markdown fences:
{"accuracy": <int>, "relevance": <int>, "coherence": <int>, "completeness": <int>, "justification": "<one sentence>"}
```

**3. Parsing**
Parse the judge's response as JSON. If parsing fails (malformed JSON), retry the judge call once with a stricter reminder appended ("Return ONLY the JSON object, nothing else"). If it fails a second time, log the row as failed and assign `None` to all scores — do not crash the run.

**4. Composite score calculation**
After parsing accuracy/relevance/coherence/completeness, compute in Python (not by the LLM):
```python
composite_score = (
    RUBRIC_WEIGHTS["accuracy"] * accuracy +
    RUBRIC_WEIGHTS["relevance"] * relevance +
    RUBRIC_WEIGHTS["coherence"] * coherence +
    RUBRIC_WEIGHTS["completeness"] * completeness
)
```
Import `RUBRIC_WEIGHTS` from `config.py` — do not hardcode weights here.

**5. Output schema**
Take every column from `raw_responses.csv` and append these columns:
```
accuracy, relevance, coherence, completeness, composite_score, justification
```
Save to `config.SCORED_RESPONSES_PATH`.

**6. Progress logging + retry**
Same style as generator.py: `[{count}/120] Judging: {model_name} | {strategy_name} | {task_category} | test_case_{i}`. Apply the same 3-retry exponential backoff on API/network failures (distinct from the JSON-parse retry in step 3).

Confirm the script produces a 120-row scored CSV with valid composite scores (spot-check that no row has a null composite_score unless it genuinely failed twice), then stop and wait for Build Prompt 4.
