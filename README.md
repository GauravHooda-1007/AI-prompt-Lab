# Prompt Optimization Laboratory 🧪

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy)

The **Prompt Optimization Laboratory** is a comprehensive, automated, research-grade benchmarking system designed to scientifically evaluate the performance of different Large Language Models (LLMs) across various prompting strategies and task categories.

Instead of relying on human intuition or manual testing, this system programmatically generates, evaluates, and aggregates results using a structured pipeline.

> **🌐 Live Demo:** *[Link will be added after deployment]*

---

## 🏗️ 1. Project Architecture

The project is decoupled into five distinct Python modules that execute linearly. Data is passed between these modules via CSV files in the `data/` directory. This decoupled architecture ensures that if one step fails (e.g., due to an API rate limit), you do not have to restart the entire pipeline from scratch.

### The Pipeline Flow:
1. **Configuration (`config.py`)** -> The source of truth.
2. **Generation (`generator.py`)** -> Creates responses.
3. **Evaluation (`judge.py`)** -> Grades responses.
4. **Aggregation (`aggregator.py`)** -> Analyzes scores.
5. **Presentation (`dashboard.py`)** -> Visualizes results interactively.

---

## 🔬 2. Experimental Design (Factorial Setup)

The laboratory runs a "full factorial" experiment, meaning it tests every single possible combination of three different variables to ensure an apples-to-apples comparison.

*   **Factor A (Models):** We test two powerful models provided by Groq:
    *   `qwen/qwen3.8-27b` (Qwen 3.8 27B — a strong mid-size reasoning model)
    *   `openai/gpt-oss-120b` (GPT-OSS 120B — a large, highly capable model)
*   **Factor B (Prompt Strategies):** Four distinct ways of prompting the AI:
    1.  **Zero-shot:** Direct instructions with no examples.
    2.  **Few-shot:** Instructions paired with two hardcoded examples to establish a pattern.
    3.  **Chain-of-Thought (CoT):** Forcing the model to "think step by step" before answering.
    4.  **Role-based:** Asking the model to act as a specific expert (e.g., an expert linguist or logician).
*   **Factor C (Task Categories):** Three distinct types of workloads:
    1.  **Classification:** Sentiment analysis of user reviews.
    2.  **Summarization:** Condensing complex paragraphs into 2-3 sentences.
    3.  **Reasoning/QA:** Solving logic and math puzzles.

For each of the 3 tasks, we have **5 fixed test cases**.
*Total Generations = 2 Models × 4 Strategies × 3 Tasks × 5 Test Cases = 120 Total Generations.*

---

## 📂 3. Minute Detail: File-by-File Breakdown

### `config.py` (The Brain)
This file holds all the static data for the project. No API calls are made here. 
- **`MODELS`**: A dictionary defining the provider and model IDs.
- **Prompt Functions**: `zero_shot`, `few_shot`, `chain_of_thought`, and `role_based`. These take in the task instruction and user input, returning the final formatted prompt.
- **`TASKS`**: A nested dictionary containing the instructions and the 5 test cases for Classification, Summarization, and Reasoning.
- **`RUBRIC_WEIGHTS`**: Defines how much each grading criterion matters (Accuracy=40%, Relevance=20%, Coherence=20%, Completeness=20%).
- **Paths**: Defines where the CSV files are saved.

### `generator.py` (The Engine)
This script loops through all 120 combinations. 
- It uses the `groq` SDK and the `tenacity` library for exponential backoff (retrying up to 3 times if an API call fails).
- It injects the test cases into the prompt templates from `config.py`.
- It calls the Groq API and saves the raw text responses, along with metadata (model, strategy, task, timestamp), to `data/raw_responses.csv`.

### `judge.py` (The Grader)
This script handles the **LLM-as-a-Judge** evaluation methodology. No human reads the 120 responses. 
- It reads `data/raw_responses.csv`.
- It uses `qwen/qwen3.8-27b` as an impartial judge.
- It passes the original instruction, the input, and the AI's generated response to the judge, asking it to score the response from 1-5 on Accuracy, Relevance, Coherence, and Completeness.
- The judge is strictly prompted to return its evaluation as a valid JSON object.
- The script parses the JSON, calculates a mathematically weighted **Composite Score** using the rubric from `config.py`, and saves the final grades to `data/scored_responses.csv`.

### `aggregator.py` (The Analyst)
A pure data manipulation script utilizing `pandas`.
- It reads the scored responses and groups the data to find insights.
- It calculates the `mean` and `std` (standard deviation) of the composite scores.
- It outputs several granular CSVs: `summary_finegrain.csv`, `summary_by_model.csv`, `summary_by_strategy.csv`, and `summary_best_combo.csv`.
- Finally, it programmatically writes a Markdown report (`findings.md`) detailing the overall winners and insights.

### `dashboard.py` (The Presentation)
A `streamlit` web application that provides a beautiful, interactive GUI for the project. It features a tabbed layout:
1. **Benchmark Results Tab**: Reads the aggregated CSVs and renders interactive Plotly bar charts and DataFrames. It features sidebar filters to drill down into specific models or tasks, and includes a "Consistency Check" that highlights high-variance (inconsistent) combinations.
2. **Live Playground Tab**: An interactive demo layer. Users can type a custom prompt, select a task and strategy, and hit "Run Comparison". The app instantly builds the prompt, queries both models live, judges them live, and declares a winner side-by-side. Crucially, this live demo does *not* write to the `data/` folder, ensuring the fixed 120-generation research benchmark remains uncontaminated.

### `.env` (Environment Variables)
Stores the `GROQ_API_KEY` required to authenticate and interact with the Groq API.

---

## 🚀 4. How to Run the Project

To execute the entire pipeline from scratch, open your terminal and run the scripts in this exact order:

1. **Set up environment:** Ensure your `GROQ_API_KEY` is present in the `.env` file.
2. **Generate Responses:** 
   ```bash
   python generator.py
   ```
   *(Wait for 120 API calls to complete. Outputs: `data/raw_responses.csv`)*
3. **Evaluate Responses:**
   ```bash
   python judge.py
   ```
   *(Wait for 120 JSON judge evaluations to complete. Outputs: `data/scored_responses.csv`)*
4. **Aggregate Data:**
   ```bash
   python aggregator.py
   ```
   *(Instantly computes math. Outputs: summary CSVs and `findings.md`)*
5. **Launch Dashboard:**
   ```bash
   streamlit run dashboard.py
   ```
   *(Opens the interactive web application in your browser)*


---

## ☁️ 5. Cloud Deployment (Streamlit Community Cloud)

This project is deployed on [Streamlit Community Cloud](https://share.streamlit.io).

To deploy your own instance:

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **"New app"** → select this repo → set main file to `dashboard.py`
4. In **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
5. Click **Deploy**

> **Note:** The Benchmark Results tab works with the pre-computed CSV data included in the repo. The Live Playground tab requires a valid Groq API key to make real-time API calls.
