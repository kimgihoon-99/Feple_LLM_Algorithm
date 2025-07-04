import pandas as pd
import numpy as np
import os

def minmax_normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def compute_politeness_score(row):
    hr = row['honorific_ratio_norm']
    pr = row['positive_word_ratio_norm']
    er = row['euphonious_word_ratio_norm']
    nr = row['negative_word_ratio_norm']
    return (hr + pr + er + (1 - nr)) / 4

def grade_from_cutoff(score, cutoffs):
    if score >= cutoffs["A"]: return "A"
    elif score >= cutoffs["B"]: return "B"
    elif score >= cutoffs["C"]: return "C"
    elif score >= cutoffs["D"]: return "D"
    elif score >= cutoffs["E"]: return "E"
    elif score >= cutoffs["F"]: return "F"
    else: return "G"

def evaluate_politeness(df):
    df = df.copy()
    df['honorific_ratio_norm'] = minmax_normalize(df['honorific_ratio'])
    df['positive_word_ratio_norm'] = minmax_normalize(df['positive_word_ratio'])
    df['negative_word_ratio_norm'] = minmax_normalize(df['negative_word_ratio'])
    df['euphonious_word_ratio_norm'] = minmax_normalize(df['euphonious_word_ratio'])
    df['Politeness_score'] = df.apply(compute_politeness_score, axis=1)
    df['percentile'] = df['Politeness_score'].rank(pct=True)
    df['Politeness_Grade'] = df['percentile'].apply(lambda p: grade_from_cutoff(p, {"A": 0.90, "B": 0.70, "C": 0.50, "D": 0.30, "E": 0.10, "F": 0.05}))
    return df[['honorific_ratio', 'positive_word_ratio', 'negative_word_ratio', 'euphonious_word_ratio',
              'Politeness_score', 'percentile', 'Politeness_Grade']]

if __name__ == "__main__":
    DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_data.csv')
    df = pd.read_csv(DATA_PATH)
    cols = ['honorific_ratio', 'positive_word_ratio', 'negative_word_ratio', 'euphonious_word_ratio']
    result = evaluate_politeness(df[cols])
    print(result.head(100))