import pandas as pd
import numpy as np
import config
import os

if not os.path.exists(config.SCORED_RESPONSES_PATH):
    print("No scored responses to mock.")
else:
    df = pd.read_csv(config.SCORED_RESPONSES_PATH)
    # Give random scores between 1 and 5
    df['accuracy'] = np.random.randint(1, 6, size=len(df))
    df['relevance'] = np.random.randint(1, 6, size=len(df))
    df['coherence'] = np.random.randint(1, 6, size=len(df))
    df['completeness'] = np.random.randint(1, 6, size=len(df))
    
    df['composite_score'] = (
        df['accuracy'] * config.RUBRIC_WEIGHTS['accuracy'] +
        df['relevance'] * config.RUBRIC_WEIGHTS['relevance'] +
        df['coherence'] * config.RUBRIC_WEIGHTS['coherence'] +
        df['completeness'] * config.RUBRIC_WEIGHTS['completeness']
    )
    
    df.to_csv(config.SCORED_RESPONSES_PATH, index=False)
    print("Mocked scores successfully.")
