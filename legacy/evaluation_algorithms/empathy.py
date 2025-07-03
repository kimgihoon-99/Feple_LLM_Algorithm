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

def grade_from_percentile(p):
    if   p >= 0.90: return "A+"
    elif p >= 0.80: return "A"
    elif p >= 0.70: return "B+"
    elif p >= 0.60: return "B"
    elif p >= 0.50: return "C+"
    elif p >= 0.40: return "C"
    else:           return "D"

def evaluate_empathy(df):
    df = df.copy()
    df['empathy_ratio_norm'] = minmax_normalize(df['empathy_ratio'])
    df['apology_ratio_norm'] = minmax_normalize(df['apology_ratio'])
    df['Empathy_score'] = df.apply(compute_empathy_score, axis=1)
    df['percentile'] = df['Empathy_score'].rank(pct=True)
    df['Empathy_Grade'] = df['percentile'].apply(grade_from_percentile)
    return df[['empathy_ratio','apology_ratio','Empathy_score','percentile','Empathy_Grade']]

if __name__ == "__main__":
    DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_data.csv')
    df = pd.read_csv(DATA_PATH)
    cols = ['empathy_ratio', 'apology_ratio']
    result = evaluate_empathy(df[cols])
    print(result.head(100))
