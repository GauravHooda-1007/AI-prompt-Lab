MODELS = {
    "qwen3-27b": {"provider": "groq", "model_id": "qwen/qwen3.8-27b"},
    "gpt-oss-120b": {"provider": "groq", "model_id": "openai/gpt-oss-120b"}
}

def zero_shot(task_instruction, input_text):
    return f"{task_instruction}\n\nInput: {input_text}"

def few_shot(task_instruction, input_text):
    if "sentiment" in task_instruction.lower():
        examples = (
            "Example 1:\nInput: I absolutely loved the service, it was fantastic!\nOutput: Positive\n\n"
            "Example 2:\nInput: The food was terribly bland and cold.\nOutput: Negative\n\n"
        )
    elif "summarize" in task_instruction.lower():
        examples = (
            "Example 1:\n"
            "Input: Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities. This chemical energy is stored in carbohydrate molecules, such as sugars and starches, which are synthesized from carbon dioxide and water.\n"
            "Output: Plants use photosynthesis to turn light energy into chemical energy. This energy is stored as carbohydrates like sugars and starches.\n\n"
        )
    else: # reasoning
        examples = (
            "Example 1:\n"
            "Input: If a train travels at 60 mph for 2 hours, how far does it go?\n"
            "Output: The train travels at 60 mph. In 2 hours, the distance is 60 * 2 = 120 miles.\n\n"
        )
    
    return f"{task_instruction}\n\n{examples}Input: {input_text}"

def chain_of_thought(task_instruction, input_text):
    return f"{task_instruction}\n\nLet's think step by step.\n\nInput: {input_text}"

def role_based(task_instruction, input_text):
    if "sentiment" in task_instruction.lower():
        role = "You are an expert linguist and customer sentiment analyst. Your task is to accurately deduce the underlying emotion of the text."
    elif "summarize" in task_instruction.lower():
        role = "You are an expert executive assistant known for creating concise and highly accurate summaries of complex information."
    else:
        role = "You are a brilliant mathematician and logician capable of solving complex multi-step reasoning problems flawlessly."
        
    return f"{role}\n\n{task_instruction}\n\nInput: {input_text}"

STRATEGIES = {
    "zero_shot": zero_shot,
    "few_shot": few_shot,
    "chain_of_thought": chain_of_thought,
    "role_based": role_based
}

TASKS = {
    "classification": {
        "instruction": "Classify the sentiment of the following text as Positive, Negative, or Neutral.",
        "test_cases": [
            "The product arrived on time and works exactly as described. I couldn't be happier with my purchase.",
            "I waited three weeks for this to ship, and when it finally arrived, the packaging was completely destroyed. The item inside is dented.",
            "The movie was okay. It had some good action scenes, but the plot was a bit predictable. Not the best, but not the worst.",
            "Customer service was incredibly helpful when I called about a billing issue. They resolved it in under five minutes!",
            "The instruction manual is extremely difficult to understand. It took me hours to assemble what should have been a 20-minute job."
        ]
    },
    "summarization": {
        "instruction": "Summarize the following passage in 2-3 sentences.",
        "test_cases": [
            "The James Webb Space Telescope (JWST) is an infrared space observatory that launched on December 25, 2021. It is the largest and most powerful space telescope ever built. JWST's high resolution and sensitivity allow it to view objects too old, distant, or faint for the Hubble Space Telescope. Its primary mission is to investigate the origins of the universe, including the formation of the first stars and galaxies.",
            "Nuclear fusion is the process by which two light atomic nuclei combine to form a single heavier one while releasing massive amounts of energy. It is the reaction that powers the sun and other stars. Scientists have been trying for decades to replicate this process on Earth to create a clean, nearly limitless source of energy, but containing the superheated plasma required for fusion remains a significant technological challenge.",
            "Artificial intelligence (AI) regulation is becoming a major priority for governments worldwide. The European Union recently passed the AI Act, which categorizes AI systems by risk level and imposes strict requirements on high-risk applications. Meanwhile, the United States is pursuing a more decentralized approach, relying on executive orders and agency-specific guidelines rather than sweeping federal legislation, sparking debates over innovation versus safety.",
            "The Mediterranean diet, characterized by high consumption of vegetables, fruits, whole grains, beans, nuts, and olive oil, is widely considered one of the healthiest diets in the world. Numerous studies have linked it to a reduced risk of heart disease, stroke, and certain types of cancer. Unlike restrictive diets, it emphasizes lifestyle factors such as eating with family and getting regular physical activity.",
            "Quantum computing represents a paradigm shift from classical computing. Instead of using bits that represent either a 0 or a 1, quantum computers use quantum bits, or qubits, which can exist in multiple states simultaneously thanks to superposition. This property, along with entanglement, theoretically allows quantum computers to solve certain complex problems—such as factoring large numbers and simulating molecular interactions—exponentially faster than the best supercomputers."
        ]
    },
    "reasoning": {
        "instruction": "Solve the following problem, showing your reasoning.",
        "test_cases": [
            "A snail is at the bottom of a 20-foot well. Every day it climbs up 5 feet, but at night it slips down 4 feet. How many days will it take for the snail to reach the top of the well?",
            "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
            "Alice, Bob, and Charlie each have a different favorite fruit: apple, banana, or cherry. Alice does not like apples. Bob's favorite fruit is banana. What is Charlie's favorite fruit?",
            "A store sells shirts for $20 each. If you buy 3 shirts, you get a 25% discount on the total price. How much will you pay if you buy 5 shirts, assuming the discount only applies to multiples of 3?",
            "In a certain town, 60% of the people own a dog, 40% own a cat, and 20% own both a dog and a cat. What percentage of the people own neither a dog nor a cat?"
        ]
    }
}

RUBRIC_WEIGHTS = {
    "accuracy": 0.4,
    "relevance": 0.2,
    "coherence": 0.2,
    "completeness": 0.2
}

DATA_DIR = "data"
RAW_RESPONSES_PATH = f"{DATA_DIR}/raw_responses.csv"
SCORED_RESPONSES_PATH = f"{DATA_DIR}/scored_responses.csv"
SUMMARY_PATH = f"{DATA_DIR}/summary_by_group.csv"
FINDINGS_PATH = "findings.md"
