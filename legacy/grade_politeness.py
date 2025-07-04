import pandas as pd
import numpy as np
import json
import os

# 1. 새로운 데이터 로드
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'new_data.csv')
df = pd.read_csv(DATA_PATH)

# 2. 기존 cut-off 불러오기
CUTOFF_PATH = os.path.join(os.path.dirname(__file__), '..', 'cutoff', 'grade_cutoff_politeness.json')
with open(CUTOFF_PATH, 'r') as f:
    cutoffs = json.load(f)

# 3. min/max 값 (cut-off 산출 당시 값으로 교체 필요)
min_hr, max_hr = 0, 100  # 실제 값으로 교체
min_pr, max_pr = 0, 100
min_er, max_er = 0, 100
min_nr, max_nr = 0, 100

def minmax_normalize(series, min_val, max_val):
    if max_val > min_val:
        return (series - min_val) / (max_val - min_val)
    else:
        return 0.5

df['honorific_ratio_norm'] = minmax_normalize(df['honorific_ratio'], min_hr, max_hr)
df['positive_word_ratio_norm'] = minmax_normalize(df['positive_word_ratio'], min_pr, max_pr)
df['euphonious_word_ratio_norm'] = minmax_normalize(df['euphonious_word_ratio'], min_er, max_er)
df['negative_word_ratio_norm'] = minmax_normalize(df['negative_word_ratio'], min_nr, max_nr)

def compute_politeness_score(row):
    hr = row['honorific_ratio_norm']
    pr = row['positive_word_ratio_norm']
    er = row['euphonious_word_ratio_norm']
    nr = row['negative_word_ratio_norm']
    return (hr + pr + er + (1 - nr)) / 4

df['Politeness_score'] = df.apply(compute_politeness_score, axis=1)

def grade_from_cutoff(score, cutoffs):
    if score >= cutoffs["A"]: return "A"
    elif score >= cutoffs["B"]: return "B"
    elif score >= cutoffs["C"]: return "C"
    elif score >= cutoffs["D"]: return "D"
    elif score >= cutoffs["E"]: return "E"
    elif score >= cutoffs["F"]: return "F"
    else: return "G"

df['Politeness_Grade'] = df['Politeness_score'].apply(lambda x: grade_from_cutoff(x, cutoffs))

print(df[['Politeness_score', 'Politeness_Grade']].head(20)) 