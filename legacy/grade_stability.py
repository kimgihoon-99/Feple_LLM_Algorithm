import pandas as pd
import numpy as np
import json
import os

# 1. 새로운 데이터 로드
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'new_data.csv')
df = pd.read_csv(DATA_PATH)

# 2. 기존 cut-off 불러오기
CUTOFF_PATH = os.path.join(os.path.dirname(__file__), '..', 'cutoff', 'grade_cutoff_stability.json')
with open(CUTOFF_PATH, 'r') as f:
    cutoffs = json.load(f)

# 3. min/max 값 (cut-off 산출 당시 값으로 교체 필요)
min_ic, max_ic = 0, 5  # 실제 값으로 교체
min_sr, max_sr = 0, 1
min_tr, max_tr = 0, 1

def minmax_normalize(series, min_val, max_val):
    if max_val > min_val:
        return (series - min_val) / (max_val - min_val)
    else:
        return 0.5

df['interruption_count_norm'] = minmax_normalize(df['interruption_count'], min_ic, max_ic)
df['silence_ratio_norm'] = minmax_normalize(df['silence_ratio'], min_sr, max_sr)
df['talk_ratio_norm'] = minmax_normalize(df['talk_ratio'], min_tr, max_tr)

def compute_stability_score(row):
    ic_norm = row['interruption_count_norm']
    sr_norm = row['silence_ratio_norm']
    tr_norm = row['talk_ratio_norm']
    interrupt_score = 1 - ic_norm
    optimal_silence = 0.25
    silence_distance = abs(sr_norm - optimal_silence)
    silence_score = max(0.0, 1 - 4 * silence_distance)
    talk_distance = abs(tr_norm - 0.5)
    talk_score = max(0.0, 1 - 2 * talk_distance)
    score = interrupt_score * 0.3 + silence_score * 0.4 + talk_score * 0.3
    return float(np.clip(score, 0.0, 1.0))

df['Stability_score'] = df.apply(compute_stability_score, axis=1)

def grade_from_cutoff(score, cutoffs):
    if score >= cutoffs["A"]: return "A"
    elif score >= cutoffs["B"]: return "B"
    elif score >= cutoffs["C"]: return "C"
    elif score >= cutoffs["D"]: return "D"
    elif score >= cutoffs["E"]: return "E"
    elif score >= cutoffs["F"]: return "F"
    else: return "G"

df['Stability_Grade'] = df['Stability_score'].apply(lambda x: grade_from_cutoff(x, cutoffs))

print(df[['Stability_score', 'Stability_Grade']].head(20)) 