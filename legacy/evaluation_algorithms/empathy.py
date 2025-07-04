import pandas as pd
import numpy as np
import os

def minmax_normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def compute_empathy_score(row):
    er = row['empathy_ratio_norm']
    ar = row['apology_ratio_norm']
    score = er * 0.7 + ar * 0.3
    return max(0.0, min(score, 1.0))

def grade_from_cutoff(score, cutoffs):
    if score >= cutoffs["A"]: return "A"
    elif score >= cutoffs["B"]: return "B"
    elif score >= cutoffs["C"]: return "C"
    elif score >= cutoffs["D"]: return "D"
    elif score >= cutoffs["E"]: return "E"
    elif score >= cutoffs["F"]: return "F"
    else: return "G"

def evaluate_empathy(df):
    df = df.copy()
    df['empathy_ratio_norm'] = minmax_normalize(df['empathy_ratio'])
    df['apology_ratio_norm'] = minmax_normalize(df['apology_ratio'])
    df['Empathy_score'] = df.apply(compute_empathy_score, axis=1)
    df['percentile'] = df['Empathy_score'].rank(pct=True)
    df['Empathy_Grade'] = df['percentile'].apply(lambda p: grade_from_cutoff(p, {"A": 0.9, "B": 0.8, "C": 0.7, "D": 0.6, "E": 0.5, "F": 0.4}))
    return df[['empathy_ratio','apology_ratio','Empathy_score','percentile','Empathy_Grade']]

if __name__ == "__main__":
    DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_data.csv')
    df = pd.read_csv(DATA_PATH)
    cols = ['empathy_ratio', 'apology_ratio']
    result = evaluate_empathy(df[cols])
    print(result.head(100))
