import os
import pandas as pd
import config

def generate_narrative(best_model_name, best_strategy_name, best_combos):
    narrative = f"The overall best performing model in this evaluation was **{best_model_name}**, while the most effective prompt strategy on average was **{best_strategy_name}**. "
    
    unique_best_strategies = set([combo['strategy'] for combo in best_combos.values()])
    
    if len(unique_best_strategies) == 1:
        narrative += f"Interestingly, the **{list(unique_best_strategies)[0]}** strategy consistently won across all task categories, suggesting it is a robust, universal 'best prompt' approach for these models. "
    else:
        narrative += "However, the best strategy varied depending on the task category. This highlights that there is no universal 'best prompt'—tailoring the prompting strategy to the specific task is crucial for optimal performance. "
        
    return narrative

def main():
    if not os.path.exists(config.SCORED_RESPONSES_PATH):
        print(f"Error: {config.SCORED_RESPONSES_PATH} not found.")
        return

    df = pd.read_csv(config.SCORED_RESPONSES_PATH)
    
    initial_len = len(df)
    df = df.dropna(subset=['composite_score'])
    dropped = initial_len - len(df)
    
    if dropped > 0:
        print(f"Dropped {dropped} rows with null composite_scores (failed judge calls).")

    if df.empty:
        print("Error: No valid rows remaining after dropping nulls. Cannot aggregate.")
        return

    # Level 1 - Fine-grained
    l1 = df.groupby(["model_name", "strategy", "task_category"])["composite_score"].agg(['mean', 'std', 'count']).reset_index()
    l1.to_csv(os.path.join(config.DATA_DIR, "summary_finegrain.csv"), index=False)

    # Level 2 - By model
    l2 = df.groupby(["model_name"])["composite_score"].agg(['mean', 'std', 'count']).reset_index()
    l2 = l2.sort_values(by="mean", ascending=False)
    l2.to_csv(os.path.join(config.DATA_DIR, "summary_by_model.csv"), index=False)
    
    best_model_row = l2.iloc[0]
    best_model_name = best_model_row['model_name']
    best_model_score = best_model_row['mean']

    # Level 3 - By strategy
    l3 = df.groupby(["strategy"])["composite_score"].agg(['mean', 'std', 'count']).reset_index()
    l3 = l3.sort_values(by="mean", ascending=False)
    l3.to_csv(os.path.join(config.DATA_DIR, "summary_by_strategy.csv"), index=False)
    
    best_strategy_row = l3.iloc[0]
    best_strategy_name = best_strategy_row['strategy']
    best_strategy_score = best_strategy_row['mean']

    # Level 4 - By task
    l4 = df.groupby(["task_category"])["composite_score"].agg(['mean', 'std', 'count']).reset_index()
    l4.to_csv(os.path.join(config.DATA_DIR, "summary_by_task.csv"), index=False)

    # Level 5 - Best combo per task
    task_model_strat = df.groupby(["task_category", "model_name", "strategy"])["composite_score"].mean().reset_index()
    best_combos = {}
    best_combo_rows = []
    
    for task in df['task_category'].unique():
        task_data = task_model_strat[task_model_strat['task_category'] == task]
        best_row = task_data.loc[task_data['composite_score'].idxmax()]
        
        best_combos[task] = {
            "model": best_row['model_name'],
            "strategy": best_row['strategy'],
            "score": best_row['composite_score']
        }
        best_combo_rows.append({
            "task_category": task,
            "best_model": best_row['model_name'],
            "best_strategy": best_row['strategy'],
            "mean_score": best_row['composite_score']
        })
        
    pd.DataFrame(best_combo_rows).to_csv(os.path.join(config.DATA_DIR, "summary_best_combo.csv"), index=False)

    # Findings generation
    narrative = generate_narrative(best_model_name, best_strategy_name, best_combos)
    
    inconsistent = l1[l1['std'] > 0.75]
    
    findings_md = f"# Prompt Optimization Laboratory — Findings\n\n"
    findings_md += f"## Overall Winners\n"
    findings_md += f"- **Best Model:** {best_model_name} (Mean Score: {best_model_score:.2f})\n"
    findings_md += f"- **Best Strategy:** {best_strategy_name} (Mean Score: {best_strategy_score:.2f})\n\n"
    
    findings_md += f"## Best Combinations per Task\n\n"
    findings_md += "| Task Category | Best Model | Best Strategy | Mean Composite Score |\n"
    findings_md += "| ------------- | ---------- | ------------- | -------------------- |\n"
    for task, data in best_combos.items():
        findings_md += f"| {task.capitalize()} | {data['model']} | {data['strategy']} | {data['score']:.2f} |\n"
    
    findings_md += f"\n## Narrative Summary\n\n"
    findings_md += f"{narrative}\n\n"
    
    if not inconsistent.empty:
        findings_md += "## Inconsistent Combinations (High Variance)\n\n"
        findings_md += "The following combinations showed unusually high standard deviations (>0.75), indicating inconsistent performance across test cases:\n"
        for _, row in inconsistent.iterrows():
            findings_md += f"- **{row['task_category']}** | {row['model_name']} | {row['strategy']} (Std: {row['std']:.2f})\n"
            
    with open(config.FINDINGS_PATH, "w", encoding="utf-8") as f:
        f.write(findings_md)

    print("\n=== AGGREGATION RESULTS ===")
    print(f"Overall Best Model: {best_model_name} ({best_model_score:.2f})")
    print(f"Overall Best Strategy: {best_strategy_name} ({best_strategy_score:.2f})")
    print("\nBest Combos per Task:")
    for task, data in best_combos.items():
        print(f"  - {task}: {data['model']} + {data['strategy']} ({data['score']:.2f})")
    print("\nFindings generated at:", config.FINDINGS_PATH)

if __name__ == "__main__":
    main()
