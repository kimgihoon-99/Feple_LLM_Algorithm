import pandas as pd
import numpy as np
import os

def minmax_normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def compute_emotional_stability_score(row):
    early = row['customer_sentiment_early_norm']
    late  = row['customer_sentiment_late_norm']
    change = late - early

    if change == 0:
        # 감정 변화 없을 때 보정
        if early < 0.4:
            raw = 0.50   # 초반이 낮아도 유지 → 중립 점수
        elif early >= 0.7:
            raw = 0.95   # 초반이 높아 유지 → 매우 안정적
        else:
            raw = 0.85   # 중간 수준 유지 → 양호
    else:
        # 변화 있을 때 기본 포뮬러
        improvement = max(change, 0.0)
        raw = late * 0.7 + improvement * 0.3

    # 0~1 범위로 클램프
    return max(0.0, min(raw, 1.0))

def grade_from_percentile(p):
    if   p >= 0.90: return "A+"
    elif p >= 0.80: return "A"
    elif p >= 0.70: return "B+"
    elif p >= 0.60: return "B"
    elif p >= 0.50: return "C+"
    elif p >= 0.40: return "C"
    else:           return "D"

def evaluate_emotional_stability(df):
    # Min-Max 정규화 적용
    df = df.copy()
    df['customer_sentiment_early_norm'] = minmax_normalize(df['customer_sentiment_early'])
    df['customer_sentiment_late_norm']  = minmax_normalize(df['customer_sentiment_late'])
    df['EmotionalStability_score'] = df.apply(compute_emotional_stability_score, axis=1)
    df['percentile'] = df['EmotionalStability_score'].rank(pct=True)
    df['EmotionalStability_Grade'] = df['percentile'].apply(grade_from_percentile)
    return df[['customer_sentiment_early','customer_sentiment_early_norm','customer_sentiment_late','customer_sentiment_late_norm','EmotionalStability_score','percentile','EmotionalStability_Grade']]

if __name__ == "__main__":
    # 데이터 경로
    DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_data.csv')
    df = pd.read_csv(DATA_PATH)
    # 필요한 컬럼만 추출
    cols = ['customer_sentiment_early', 'customer_sentiment_late']
    result = evaluate_emotional_stability(df[cols])
    print(result)
