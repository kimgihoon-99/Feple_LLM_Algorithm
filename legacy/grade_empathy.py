import pandas as pd
import numpy as np
import json
import os

# 1. 새로운 데이터 로드
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'new_data.csv')
df = pd.read_csv(DATA_PATH)

# 2. 기존 cut-off 불러오기
CUTOFF_PATH = os.path.join(os.path.dirname(__file__), '..', 'cutoff', 'grade_cutoff_empathy.json')
with open(CUTOFF_PATH, 'r') as f:
    cutoffs = json.load(f)

# 3. min/max 값 (cut-off 산출 당시 값으로 교체 필요)
min_er, max_er = 0, 100  # 실제 값으로 교체
min_ar, max_ar = 0, 100

def minmax_normalize(series, min_val, max_val):
    if max_val > min_val:
        return (series - min_val) / (max_val - min_val)
    else:
        return 0.5

df['empathy_ratio_norm'] = minmax_normalize(df['empathy_ratio'], min_er, max_er)
df['apology_ratio_norm'] = minmax_normalize(df['apology_ratio'], min_ar, max_ar)

def compute_empathy_score(row):
    er = row['empathy_ratio_norm']
    ar = row['apology_ratio_norm']
    return er * 0.7 + ar * 0.3

df['Empathy_score'] = df.apply(compute_empathy_score, axis=1)

def grade_from_cutoff(score, cutoffs):
    if score >= cutoffs["A+"]: return "A+"
    elif score >= cutoffs["A"]: return "A"
    elif score >= cutoffs["B+"]: return "B+"
    elif score >= cutoffs["B"]: return "B"
    elif score >= cutoffs["C+"]: return "C+"
    elif score >= cutoffs["C"]: return "C"
    else: return "D"

df['Empathy_Grade'] = df['Empathy_score'].apply(lambda x: grade_from_cutoff(x, cutoffs))

print(df[['Empathy_score', 'Empathy_Grade']].head(20)) 