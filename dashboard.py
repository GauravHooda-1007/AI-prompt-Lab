import streamlit as st
import pandas as pd
import plotly.express as px
import config
import os

from generator import call_groq
from judge import call_judge_api, parse_judge_response

# 1. Page setup
st.set_page_config(page_title="Prompt Optimization Laboratory", layout="wide")
st.title("Prompt Optimization Laboratory — Comparative Response Quality Evaluation")
st.markdown("A factorial benchmarking system evaluating how well different LLMs perform under different prompting strategies across different task categories (2 models × 4 strategies × 3 tasks × 5 test cases).")

# Load data
@st.cache_data
def load_data():
    try:
        finegrain = pd.read_csv(os.path.join(config.DATA_DIR, "summary_finegrain.csv"))
        by_model = pd.read_csv(os.path.join(config.DATA_DIR, "summary_by_model.csv"))
        by_strategy = pd.read_csv(os.path.join(config.DATA_DIR, "summary_by_strategy.csv"))
        best_combo = pd.read_csv(os.path.join(config.DATA_DIR, "summary_best_combo.csv"))
        raw_scored = pd.read_csv(config.SCORED_RESPONSES_PATH)
        return finegrain, by_model, by_strategy, best_combo, raw_scored
    except FileNotFoundError:
        return None, None, None, None, None

finegrain, by_model, by_strategy, best_combo, raw_scored = load_data()

def render_benchmark_view():
    if finegrain is None:
        st.error("Data files not found. Please ensure you have run the generator, judge, and aggregator scripts first.")
        return
        
    # 2. Sidebar filters
    st.sidebar.header("Filters (Benchmark View)")
    selected_models = st.sidebar.multiselect("Select Model", options=finegrain['model_name'].unique(), default=finegrain['model_name'].unique())
    selected_strategies = st.sidebar.multiselect("Select Strategy", options=finegrain['strategy'].unique(), default=finegrain['strategy'].unique())
    selected_tasks = st.sidebar.multiselect("Select Task Category", options=finegrain['task_category'].unique(), default=finegrain['task_category'].unique())

    # Apply filters to finegrain and raw data
    filtered_finegrain = finegrain[
        (finegrain['model_name'].isin(selected_models)) &
        (finegrain['strategy'].isin(selected_strategies)) &
        (finegrain['task_category'].isin(selected_tasks))
    ]

    filtered_raw = raw_scored[
        (raw_scored['model_name'].isin(selected_models)) &
        (raw_scored['strategy'].isin(selected_strategies)) &
        (raw_scored['task_category'].isin(selected_tasks))
    ]

    # 3. Section 1 - Leaderboard
    st.header("Overall Leaderboards")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("By Model")
        st.dataframe(by_model.sort_values(by="mean", ascending=False), use_container_width=True)
        
    with col2:
        st.subheader("By Strategy")
        st.dataframe(by_strategy.sort_values(by="mean", ascending=False), use_container_width=True)

    # 4. Section 2 - Best Combo Per Task
    st.header("Best Combination per Task")
    st.dataframe(best_combo, use_container_width=True)

    # 5. Section 3 - Bar chart by task category
    st.header("Performance Comparison")
    if not filtered_finegrain.empty:
        fig = px.bar(
            filtered_finegrain, 
            x="task_category", 
            y="mean", 
            color="strategy", 
            barmode="group",
            facet_col="model_name",
            hover_data=["std"],
            labels={"mean": "Mean Composite Score", "task_category": "Task Category", "strategy": "Strategy"},
            title="Composite Score by Task and Strategy"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data matches the selected filters.")

    # 6. Section 4 - Consistency check
    st.header("Consistency Check (High Variance)")
    inconsistent = filtered_finegrain[filtered_finegrain['std'] > 0.75]
    if not inconsistent.empty:
        st.warning("The following combinations showed unusually high standard deviations (>0.75), indicating inconsistent performance across test cases:")
        st.dataframe(inconsistent, use_container_width=True)
    else:
        st.success("No high variance (std > 0.75) combinations found for the current selection. Performance is relatively consistent.")

    # 7. Section 5 - Raw data explorer
    st.header("Raw Data Explorer")
    with st.expander("View raw scored data"):
        st.dataframe(filtered_raw, use_container_width=True)

    st.markdown("---")
    st.caption("Data generated via factorial benchmarking across Groq models (Llama 3 8B and Llama 3 70B), 4 prompting strategies, 3 task categories, 5 test cases per cell (n=120).")

def render_playground_view():
    st.caption("This is a live demo, separate from the fixed 120-generation benchmark. Results here are not included in the research findings.")
    
    task_type = st.selectbox("Task type", options=list(config.TASKS.keys()))
    strategy_type = st.selectbox("Prompt strategy", options=list(config.STRATEGIES.keys()))
    user_input = st.text_area("Enter your prompt input", height=150)
    
    if st.button("Run Comparison"):
        if not user_input.strip():
            st.error("Please enter some input text.")
            return
            
        task_instruction = config.TASKS[task_type]["instruction"]
        strategy_fn = config.STRATEGIES[strategy_type]
        prompt = strategy_fn(task_instruction, user_input)
        
        with st.spinner("Running both models..."):
            llama8b_response = "ERROR"
            llama_response = "ERROR"
            
            try:
                llama8b_response = call_groq(prompt, config.MODELS["llama3-8b"]["model_id"])
            except Exception as e:
                st.error(f"Llama 3 8B failed: {e}")
                
            try:
                llama_response = call_groq(prompt, config.MODELS["llama3-70b"]["model_id"])
            except Exception as e:
                st.error(f"Llama 3 failed: {e}")
                
        def judge_response(resp_text):
            if resp_text == "ERROR" or not resp_text:
                return None
            
            base_prompt = f"""You are an impartial evaluator. Score the following AI response on a scale of 1-5 for each criterion.

TASK INSTRUCTION: {task_instruction}
INPUT: {user_input}
AI RESPONSE: {resp_text}

Score on:
1. accuracy (1-5): factual/logical correctness
2. relevance (1-5): does it address what was asked
3. coherence (1-5): clarity and structure
4. completeness (1-5): does it fully answer

Respond with ONLY valid JSON, no other text, no markdown fences:
{{"accuracy": <int>, "relevance": <int>, "coherence": <int>, "completeness": <int>, "justification": "<one sentence>"}}"""
            
            try:
                judge_out = call_judge_api(base_prompt)
                parsed = parse_judge_response(judge_out)
                
                comp = (
                    parsed['accuracy'] * config.RUBRIC_WEIGHTS['accuracy'] +
                    parsed['relevance'] * config.RUBRIC_WEIGHTS['relevance'] +
                    parsed['coherence'] * config.RUBRIC_WEIGHTS['coherence'] +
                    parsed['completeness'] * config.RUBRIC_WEIGHTS['completeness']
                )
                parsed['composite_score'] = comp
                return parsed
            except Exception as e:
                st.error(f"Judge parsing failed: {e}")
                return None

        with st.spinner("Judging responses..."):
            llama8b_scores = judge_response(llama8b_response)
            llama_scores = judge_response(llama_response)
            
        col1, col2 = st.columns(2)
        
        def display_result(title, text, scores):
            st.subheader(title)
            st.write(text)
            if scores:
                st.metric("Composite Score", f"{scores['composite_score']:.2f}")
                st.json(scores)
            else:
                st.error("Scoring failed or model errored.")
                
        with col1:
            display_result("Llama 3 (8B)", llama8b_response, llama8b_scores)
            
        with col2:
            display_result("Llama 3 (70B)", llama_response, llama_scores)
            
        if llama8b_scores and llama_scores:
            if llama8b_scores['composite_score'] > llama_scores['composite_score']:
                st.success(f"🏆 Llama 3 (8B) scored higher ({llama8b_scores['composite_score']:.2f} vs {llama_scores['composite_score']:.2f})")
            elif llama_scores['composite_score'] > llama8b_scores['composite_score']:
                st.success(f"🏆 Llama 3 (70B) scored higher ({llama_scores['composite_score']:.2f} vs {llama8b_scores['composite_score']:.2f})")
            else:
                st.info(f"🤝 Both models tied ({llama8b_scores['composite_score']:.2f})")

tab1, tab2 = st.tabs(["Benchmark Results", "Live Playground"])

with tab1:
    render_benchmark_view()
    
with tab2:
    render_playground_view()
