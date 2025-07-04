import pandas as pd
import numpy as np
import json
import os

# 1. 새로운 데이터 로드
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'new_data.csv')
df = pd.read_csv(DATA_PATH)

# 2. 기존 cut-off 불러오기
CUTOFF_PATH = os.path.join(os.path.dirname(__file__), '..', 'cutoff', 'grade_cutoff_emotional_stability.json')
with open(CUTOFF_PATH, 'r') as f:
    cutoffs = json.load(f)

# 3. min/max 값 (cut-off 산출 당시 값으로 교체 필요)
min_early, max_early = 0, 1  # 실제 값으로 교체
min_late, max_late = 0, 1

def minmax_normalize(series, min_val, max_val):
    if max_val > min_val:
        return (series - min_val) / (max_val - min_val)
    else:
        return 0.5

df['customer_sentiment_early_norm'] = minmax_normalize(df['customer_sentiment_early'], min_early, max_early)
df['customer_sentiment_late_norm'] = minmax_normalize(df['customer_sentiment_late'], min_late, max_late)

def compute_emotional_stability_score(row):
    early = row['customer_sentiment_early_norm']
    late  = row['customer_sentiment_late_norm']
    change = late - early
    if change == 0:
        if early < 0.4:
            raw = 0.50
        elif early >= 0.7:
            raw = 0.95
        else:
            raw = 0.85
    else:
        improvement = max(change, 0.0)
        raw = late * 0.7 + improvement * 0.3
    return max(0.0, min(raw, 1.0))

df['EmotionalStability_score'] = df.apply(compute_emotional_stability_score, axis=1)

def grade_from_cutoff(score, cutoffs):
    if score >= cutoffs["A"]: return "A"
    elif score >= cutoffs["B"]: return "B"
    elif score >= cutoffs["C"]: return "C"
    elif score >= cutoffs["D"]: return "D"
    elif score >= cutoffs["E"]: return "E"
    elif score >= cutoffs["F"]: return "F"
    else: return "G"

df['EmotionalStability_Grade'] = df['EmotionalStability_score'].apply(lambda x: grade_from_cutoff(x, cutoffs))

print(df[['EmotionalStability_score', 'EmotionalStability_Grade']].head(20)) 