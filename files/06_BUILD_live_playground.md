# BUILD PROMPT 6 of 6 (OPTIONAL) — Live Comparison Playground

This is an ADDITION to the existing `dashboard.py`, not a replacement. The fixed 120-generation benchmark (config → generator → judge → aggregator → dashboard) stays exactly as built. This adds a second, separate page/tab to the Streamlit app where a user can type their own input and get a live, on-the-spot comparison. This is a demo layer — its results are NOT added to the research benchmark data or the summary CSVs.

## Requirements:

**1. Navigation**
Add a sidebar radio or `st.tabs` at the top of `dashboard.py` with two views:
- **"Benchmark Results"** — the existing leaderboard/charts/findings view already built
- **"Live Playground"** — the new interactive view described below

Keep them as clearly separated functions, e.g. `render_benchmark_view()` and `render_playground_view()`, so neither interferes with the other.

**2. Playground inputs (user-facing, in the UI)**
- A text area: "Enter your prompt input"
- A dropdown: "Task type" → Classification / Summarization / Reasoning-QA (used only to pick the right instruction wrapper, reusing `TASKS[...]["instruction"]` from `config.py`)
- A dropdown: "Prompt strategy" → Zero-shot / Few-shot / Chain-of-Thought / Role-based (reusing `STRATEGIES` from `config.py`)
- A button: "Run Comparison"

**3. On button click**
- Build the final prompt using the selected strategy function + selected task instruction + the user's typed input (reuse `config.py` functions — do not duplicate template logic)
- Call both `call_openai()` and `call_groq()` live (reuse functions from `generator.py` — import them, don't rewrite)
- Call the judge (reuse the judge function from `judge.py`) on both live responses using the same rubric and weights from `config.py`
- Show a spinner (`st.spinner("Running both models...")`) while waiting — this will take a few seconds

**4. Results display**
Two side-by-side columns:
- Left: "GPT-4o-mini" response text + its 4 rubric scores + composite score
- Right: "Llama 3 (70B)" response text + its 4 rubric scores + composite score
Below both: a one-line verdict, e.g. "🏆 GPT-4o-mini scored higher (4.2 vs 3.6)" computed by simple comparison of the two composite scores.

**5. Error handling**
If either API call fails (timeout, rate limit, bad key), show `st.error("...")` with the specific failure rather than crashing the whole app. The other model's result should still display if only one fails.

**6. Important constraint — do not contaminate the research data**
This view must NOT write to `data/raw_responses.csv`, `data/scored_responses.csv`, or any summary CSV. It's a live, ephemeral demo per session — nothing here should feed back into the fixed benchmark's findings.md or aggregated stats. If you want session history, keep it in `st.session_state` only (resets on refresh), optionally with a small in-page table showing the last 5 live comparisons run in the current session.

**7. Caption**
Add a small caption under the Playground tab: "This is a live demo, separate from the fixed 120-generation benchmark. Results here are not included in the research findings."

Confirm both tabs run without breaking each other, then the full 6-module pipeline is complete: config → generator → judge → aggregator → dashboard (benchmark view + live playground view).
