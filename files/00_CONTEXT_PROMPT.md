# CONTEXT PROMPT — Paste this first, before any build prompt

You are acting as a senior ML engineer building a research-grade benchmarking system called the **Prompt Optimization Laboratory**. Read this entire brief and hold it in memory before writing any code. Do not generate code yet — this message is context only. Wait for the next message which will contain the first build instruction.

## 1. Project Title
Prompt Optimization Laboratory for Comparative Response Quality Evaluation

## 2. Purpose
A factorial benchmarking system that systematically evaluates how well different LLMs perform under different prompting strategies across different task categories, using a third LLM as an automated judge, then aggregates and visualizes the results.

## 3. Technologies
- OpenAI API (e.g. `gpt-4o-mini`)
- Llama 3 (via Groq API — `llama3-70b-8192` — or local Ollama if no API key is available)
- Prompt Templates (stored as structured data, not hardcoded strings)
- pandas for aggregation
- Streamlit for the dashboard

## 4. Experimental Design (Factorial)

**Factor A — Models (2 levels):**
1. OpenAI GPT-4o-mini
2. Llama 3 (70B, via Groq)

**Factor B — Prompt Strategies (4 levels):**
1. Zero-shot — direct instruction, no examples
2. Few-shot — instruction + 2-3 worked examples
3. Chain-of-Thought (CoT) — instruction + "think step by step" scaffold
4. Role-based persona — instruction wrapped in an expert persona framing

**Factor C — Task Categories (3 levels):**
1. Classification (e.g. sentiment/topic labeling)
2. Summarization (e.g. condense a passage)
3. Reasoning/QA (e.g. multi-step logic or math word problems)

**Test cases per cell:** 5 fixed test inputs per task category (same 5 inputs reused across all model×strategy combinations for that category, so comparisons are apples-to-apples)

**Total generations = 2 models × 4 strategies × 3 tasks × 5 test cases = 120 generations**

This is a **full factorial design**: every model is tested with every strategy on every task, so we can isolate the effect of each factor independently (e.g. "does CoT help reasoning more than classification?" or "is Llama 3 more sensitive to prompt strategy than GPT-4o-mini?").

## 5. Scoring Logic — LLM-as-Judge

A third LLM call (the "judge," recommend using GPT-4o-mini or a separate model from the two being tested to reduce self-preference bias) scores every one of the 120 generations against a fixed rubric. The judge must return **strict JSON**, not free text, so it can be parsed programmatically.

**Rubric — 4 criteria, each scored 1–5:**
1. **Accuracy/Correctness** — is the answer factually/logically correct?
2. **Relevance** — does it address what was actually asked?
3. **Coherence/Clarity** — is it well-structured and easy to follow?
4. **Completeness** — does it fully answer, or leave gaps?

**Composite score formula (weighted average):**
```
composite_score = (0.4 × accuracy) + (0.2 × relevance) + (0.2 × coherence) + (0.2 × completeness)
```
Weights sum to 1.0. Accuracy is weighted highest because a fluent but wrong answer should score low overall — this prevents coherent-but-incorrect responses from ranking well.

Composite score range: 1.0 to 5.0.

**Judge output schema (per generation):**
```json
{
  "accuracy": <int 1-5>,
  "relevance": <int 1-5>,
  "coherence": <int 1-5>,
  "completeness": <int 1-5>,
  "composite_score": <float, computed by formula above>,
  "justification": "<one sentence>"
}
```

## 6. Aggregation Math (deliberately simplified — no Elo)

We are **not** using Elo pairwise ranking. Elo requires iterative head-to-head matches and converges over many rounds — unnecessary complexity for a static 120-generation benchmark. Instead:

For each grouping level, compute:
- **mean composite score** (`.mean()`)
- **standard deviation** (`.std()`) — measures consistency across the 5 test cases

**Grouping levels required:**
1. By (Model × Strategy × Task) — the finest grain, 24 groups of 5 scores each
2. By Model only — collapse across strategy & task → overall model ranking
3. By Strategy only — collapse across model & task → overall strategy ranking
4. By Task only — collapse across model & strategy → task difficulty comparison
5. **Best combo per task** — for each of the 3 tasks, find the (Model, Strategy) pair with the highest mean composite score (simple `argmax`, not iterative)

All aggregation is plain `pandas.groupby(...).agg(['mean', 'std'])` — no custom statistical machinery needed.

## 7. Pipeline Architecture (5 modules, built sequentially)

```
config.py       → static data: model list, strategy prompt templates, task test-cases
generator.py    → loops through all 120 combinations, calls both LLM APIs, saves raw responses
judge.py        → loops through all 120 raw responses, calls judge LLM, parses + saves scores
aggregator.py   → loads scored data, runs groupby math above, exports summary CSVs + findings.md
dashboard.py    → Streamlit app reading the summary CSVs, renders leaderboard + charts
```

Each module reads/writes to a shared `/data` folder using CSV or JSON so modules stay decoupled and can be re-run independently (e.g. re-running the judge without re-generating responses).

## 8. Final Deliverables
1. `data/raw_responses.csv` — all 120 raw generations
2. `data/scored_responses.csv` — raw responses + judge scores
3. `data/summary_by_group.csv` — all 5 aggregation levels
4. `findings.md` — auto-generated markdown summary: overall winner model, overall winner strategy, best combo per task, one-paragraph narrative
5. `dashboard.py` — interactive Streamlit leaderboard + bar charts by task category

## 9. Environment Notes for Antigravity
- Use `.env` for API keys (`OPENAI_API_KEY`, `GROQ_API_KEY`) — never hardcode keys
- Add retry logic (max 3 retries, exponential backoff) around every API call — 120+ calls means transient failures are likely
- Add a small delay/rate-limit guard between calls if needed
- Log progress to console (e.g. `"[12/120] GPT-4o-mini | Few-shot | Summarization | test_case_3"`) so long runs are observable

---
**Acknowledge that you understand this full project brief. Do not write any code in response to this message — wait for the next message, which will be Build Prompt 1 (config.py).**
