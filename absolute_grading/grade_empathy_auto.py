import pandas as pd
import json
import os
import numpy as np
import sys

def clip_outliers_iqr(df, cols):
    for col in cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        df[col] = df[col].clip(lower, upper)
    return df

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'new_data.csv')
DUMMY_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_data.csv')
if os.path.exists(DATA_PATH):
    print(f"[INFO] new_data.csv로 평가를 진행합니다.")
    eval_path = DATA_PATH
else:
    print(f"[INFO] new_data.csv가 없어 dummy_data.csv로 평가를 진행합니다.")
    eval_path = DUMMY_PATH

CUTOFF_PATH = os.path.join(os.path.dirname(__file__), '..', 'cutoff', 'grade_cutoff_empathy.json')
cols = ['empathy_ratio', 'apology_ratio']

eval_df = pd.read_csv(eval_path)
eval_df.columns = eval_df.columns.str.strip()
eval_df = clip_outliers_iqr(eval_df, cols)

with open(CUTOFF_PATH) as f:
    cutoff_json = json.load(f)
    cutoffs = cutoff_json['cutoff']
    old_minmax = cutoff_json['minmax']
new_minmax = {col: {"min": float(eval_df[col].min()), "max": float(eval_df[col].max())} for col in cols}

def check_minmax(new_minmax, old_minmax):
    for key in new_minmax:
        if new_minmax[key]['min'] < old_minmax[key]['min'] or new_minmax[key]['max'] > old_minmax[key]['max']:
            return False
    return True

def minmax_normalize(series, min_val, max_val):
    if max_val > min_val:
        return (series - min_val) / (max_val - min_val)
    else:
        return 0.5

def compute_empathy_score(row):
    er = row['empathy_ratio_norm']
    ar = row['apology_ratio_norm']
    return er * 0.7 + ar * 0.3

def grade_from_cutoff(score, cutoffs):
    if score >= cutoffs["A"]: return "A"
    elif score >= cutoffs["B"]: return "B"
    elif score >= cutoffs["C"]: return "C"
    elif score >= cutoffs["D"]: return "D"
    elif score >= cutoffs["E"]: return "E"
    elif score >= cutoffs["F"]: return "F"
    else: return "G"

if check_minmax(new_minmax, old_minmax):
    print('기존 cut-off/minmax로 평가')
    minmax = old_minmax
else:
    print('범위 벗어남 → cut-off/minmax 재산출')
    old_df = pd.read_csv(DUMMY_PATH)
    old_df.columns = old_df.columns.str.strip()
    all_df = pd.concat([old_df, eval_df], ignore_index=True)
    all_df = clip_outliers_iqr(all_df, cols)
    minmax = {col: {"min": float(all_df[col].min()), "max": float(all_df[col].max())} for col in cols}
    scores = []
    for _, row in all_df.iterrows():
        er = minmax_normalize(row['empathy_ratio'], minmax['empathy_ratio']['min'], minmax['empathy_ratio']['max'])
        ar = minmax_normalize(row['apology_ratio'], minmax['apology_ratio']['min'], minmax['apology_ratio']['max'])
        score = er * 0.7 + ar * 0.3
        scores.append(score)
    new_cutoff = {
        "A": float(np.percentile(scores, 90)),
        "B":  float(np.percentile(scores, 80)),
        "C": float(np.percentile(scores, 70)),
        "D":  float(np.percentile(scores, 60)),
        "E": float(np.percentile(scores, 50)),
        "F":  float(np.percentile(scores, 40)),
        "G":  -1e9
    }
    with open(CUTOFF_PATH, 'w') as f:
        json.dump({'cutoff': new_cutoff, 'minmax': minmax}, f, indent=2)
    cutoffs = new_cutoff

for col in cols:
    eval_df[f'{col}_norm'] = minmax_normalize(eval_df[col], minmax[col]['min'], minmax[col]['max'])
eval_df['Empathy_score'] = eval_df.apply(compute_empathy_score, axis=1)
eval_df['Empathy_Grade'] = eval_df['Empathy_score'].apply(lambda x: grade_from_cutoff(x, cutoffs))

print(eval_df[['Empathy_score', 'Empathy_Grade']].head(20))

def evaluate_empathy(df):
    cols = ['empathy_ratio', 'apology_ratio']
    with open(CUTOFF_PATH) as f:
        cutoff_json = json.load(f)
        cutoffs = cutoff_json['cutoff']
        minmax = cutoff_json['minmax']
    df = clip_outliers_iqr(df.copy(), cols)
    for col in cols:
        df[f'{col}_norm'] = minmax_normalize(df[col], minmax[col]['min'], minmax[col]['max'])
    df['Empathy_score'] = df.apply(compute_empathy_score, axis=1)
    df['Empathy_Grade'] = df['Empathy_score'].apply(lambda x: grade_from_cutoff(x, cutoffs))
    return df[['Empathy_score', 'Empathy_Grade']] 