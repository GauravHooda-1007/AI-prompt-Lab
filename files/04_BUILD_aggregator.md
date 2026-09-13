# BUILD PROMPT 4 of 5 — aggregator.py

Build `aggregator.py`. This module reads `data/scored_responses.csv` and produces all aggregation levels plus a human-readable findings summary. Pure pandas — no Elo, no iterative logic.

## Requirements:

**1. Load data**
Read `config.SCORED_RESPONSES_PATH` into a DataFrame. Drop any rows where `composite_score` is null (failed judge calls) and log how many were dropped.

**2. Five aggregation levels — each as `.groupby(...).agg(['mean', 'std', 'count'])` on `composite_score`:**

- **Level 1 — Fine-grained:** group by `["model_name", "strategy", "task_category"]` (24 groups)
- **Level 2 — By model:** group by `["model_name"]` only → overall model ranking
- **Level 3 — By strategy:** group by `["strategy"]` only → overall strategy ranking
- **Level 4 — By task:** group by `["task_category"]` only → task difficulty comparison
- **Level 5 — Best combo per task:** for each `task_category`, find the `(model_name, strategy)` pair with the highest mean composite_score — use `.groupby(["task_category","model_name","strategy"])["composite_score"].mean()` then `.idxmax()` within each task group

**3. Save combined summary**
Concatenate or clearly label all 5 levels (e.g. add a `level` column indicating which grouping it belongs to) and save to `config.SUMMARY_PATH` as one CSV, OR save as separate clearly-named CSVs in `data/` (e.g. `summary_finegrain.csv`, `summary_by_model.csv`, `summary_by_strategy.csv`, `summary_by_task.csv`, `summary_best_combo.csv`). Pick whichever is cleaner for a Streamlit app to consume — your call, but be consistent.

**4. Auto-generate findings.md**
Write a markdown file to `config.FINDINGS_PATH` with:
- Title: "# Prompt Optimization Laboratory — Findings"
- Overall best model (highest Level 2 mean) with its score
- Overall best strategy (highest Level 3 mean) with its score
- A table: Task Category | Best Model | Best Strategy | Mean Composite Score (from Level 5)
- A short (3-5 sentence) auto-generated narrative paragraph interpreting the results, e.g. noting if one strategy consistently wins across tasks, or if the best strategy changes per task (which would suggest no universal "best prompt" exists)
- A note on standard deviation: flag any (model, strategy, task) combo with unusually high std (e.g. > 0.75) as "inconsistent" in a short bullet list

**5. Print a console summary**
Print the same headline findings (best model, best strategy, best combo per task) to console when the script runs, so results are visible without opening the file.

Confirm findings.md reads clearly and all summary CSVs are present in `data/`, then stop and wait for Build Prompt 5.
