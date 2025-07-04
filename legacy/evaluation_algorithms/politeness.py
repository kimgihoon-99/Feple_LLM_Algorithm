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

def grade_from_percentile(p):
    if   p >= 0.90: return "A"
    elif p >= 0.80: return "B"
    elif p >= 0.70: return "C"
    elif p >= 0.60: return "D"
    elif p >= 0.50: return "E"
    elif p >= 0.40: return "F"
    else:           return "G"

def evaluate_politeness(df):
    df = df.copy()
    df['honorific_ratio_norm'] = minmax_normalize(df['honorific_ratio'])
    df['positive_word_ratio_norm'] = minmax_normalize(df['positive_word_ratio'])
    df['negative_word_ratio_norm'] = minmax_normalize(df['negative_word_ratio'])
    df['euphonious_word_ratio_norm'] = minmax_normalize(df['euphonious_word_ratio'])
    df['Politeness_score'] = df.apply(compute_politeness_score, axis=1)
    df['percentile'] = df['Politeness_score'].rank(pct=True)
    df['Politeness_Grade'] = df['percentile'].apply(grade_from_percentile)
    return df[['honorific_ratio', 'positive_word_ratio', 'negative_word_ratio', 'euphonious_word_ratio',
              'Politeness_score', 'percentile', 'Politeness_Grade']]

if __name__ == "__main__":
    DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_data.csv')
    df = pd.read_csv(DATA_PATH)
    cols = ['honorific_ratio', 'positive_word_ratio', 'negative_word_ratio', 'euphonious_word_ratio']
    result = evaluate_politeness(df[cols])
    print(result.head(100))