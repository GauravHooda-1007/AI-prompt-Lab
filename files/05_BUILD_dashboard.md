# BUILD PROMPT 5 of 5 — dashboard.py

Build `dashboard.py`, a Streamlit app that reads the summary CSVs produced by `aggregator.py` (do not recompute aggregation logic here — just load and display). This is the final deliverable module.

## Requirements:

**1. Page setup**
`st.set_page_config(page_title="Prompt Optimization Laboratory", layout="wide")`. Title: "Prompt Optimization Laboratory — Comparative Response Quality Evaluation". One-line subtitle explaining the 2×4×3 factorial design.

**2. Sidebar filters**
- Multiselect for Model
- Multiselect for Strategy
- Multiselect for Task Category
These should filter the fine-grained summary table/charts live.

**3. Section 1 — Leaderboard**
Two side-by-side tables (`st.columns(2)`):
- Left: Overall model ranking (Level 2 summary), sorted descending by mean composite score
- Right: Overall strategy ranking (Level 3 summary), sorted descending by mean composite score

**4. Section 2 — Best Combo Per Task**
A table showing, for each task category, the winning (model, strategy) pair and its mean score (Level 5 summary). Highlight the top score per row using `st.dataframe` with conditional styling if straightforward, otherwise a plain table is fine.

**5. Section 3 — Bar chart by task category**
A grouped bar chart: x-axis = task category, bars grouped/colored by strategy (or model — pick one, but let the sidebar filter control which), y-axis = mean composite score. Use `st.bar_chart` or a `plotly` grouped bar chart if you want hover tooltips — plotly preferred if available in the environment.

**6. Section 4 — Consistency check**
A small table showing any (model, strategy, task) combos flagged as high-std ("inconsistent") from findings.md logic, OR recompute the >0.75 std flag directly from the fine-grained summary CSV.

**7. Section 5 — Raw data explorer**
An expandable section (`st.expander("View raw scored data")`) showing the full filtered `scored_responses.csv` in a scrollable `st.dataframe`.

**8. Footer**
Small caption: "Data generated via factorial benchmarking across OpenAI GPT-4o-mini and Llama 3 (70B), 4 prompting strategies, 3 task categories, 5 test cases per cell (n=120)."

**9. Run instructions**
Confirm the app runs with `streamlit run dashboard.py` and loads without errors when the `data/` CSVs from prior steps are present.

This completes the 5-module pipeline. After this step, do a final end-to-end check: config → generator → judge → aggregator → dashboard, confirming each file only depends on the ones before it and no circular imports exist.
