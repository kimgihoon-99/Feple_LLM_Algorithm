import pandas as pd
import numpy as np
import os

def minmax_normalize(series: pd.Series) -> pd.Series:
    """
    Min-Max 정규화: 각 값 x를 (x - min) / (max - min)로 변환.
    값이 모두 동일할 경우 0.5로 고정.
    """
    min_val = series.min()
    max_val = series.max()
    if max_val > min_val:
        return (series - min_val) / (max_val - min_val)
    else:
        return pd.Series(0.5, index=series.index)

def compute_stability_score_row(ic_norm: float, sr_norm: float, tr_norm: float) -> float:
    """
    정규화된 feature 값들로 대화 안정성 점수 계산.
    
    ic_norm: 정규화된 interruption_count (0~1)
    sr_norm: 정규화된 silence_ratio (0~1)  
    tr_norm: 정규화된 talk_ratio (0~1)
    
    - interruption: 낮을수록 좋음 → (1 - ic_norm)
    - silence: 적절한 수준(0.2~0.3)이 좋음 → 거리 기반 점수
    - talk: 균형(0.5)에 가까울수록 좋음 → 거리 기반 점수
    """
    # 1) 끊김 점수: 낮을수록 좋음
    interrupt_score = 1 - ic_norm
    
    # 2) 침묵 점수: 0.25 근처가 최적 (너무 적어도, 많아도 안 좋음)
    optimal_silence = 0.25
    silence_distance = abs(sr_norm - optimal_silence)
    silence_score = max(0.0, 1 - 4 * silence_distance)  # 거리의 4배만큼 페널티
    
    # 3) 발화 비율 점수: 0.5 근처가 최적 (균형)
    talk_distance = abs(tr_norm - 0.5)
    talk_score = max(0.0, 1 - 2 * talk_distance)  # 거리의 2배만큼 페널티
    
    # 가중합: 끊김(30%) + 침묵(40%) + 발화비율(30%)
    score = interrupt_score * 0.3 + silence_score * 0.4 + talk_score * 0.3
    return float(np.clip(score, 0.0, 1.0))

def grade_from_percentile(p: float) -> str:
    """
    백분위(p)에 따라 A+, A, B+, B, C+, C, D 등급 반환.
    """
    if p >= 0.90: return "A+"
    if p >= 0.70: return "A"
    if p >= 0.50: return "B+"
    if p >= 0.30: return "B"
    if p >= 0.15: return "C+"
    if p >= 0.05: return "C"
    return "D"

def compute_stability_score_and_grade(
    data: list[dict],
    return_all: bool = False
):
    """
    대화 흐름 및 응대 태도 안정성 점수 및 등급 계산 함수.

    Args:
        data: [{'interruption_count': int, 'silence_ratio': float, 'talk_ratio': float}, ...]
        return_all: False면 첫 세션 결과, True면 모든 세션 리스트 반환.

    Returns:
        (score, grade) or (scores_list, grades_list)
    """
    df = pd.DataFrame(data)
    
    # 1) Min-Max 정규화
    df['interruption_count_norm'] = minmax_normalize(df['interruption_count'])
    df['silence_ratio_norm'] = minmax_normalize(df['silence_ratio'])
    df['talk_ratio_norm'] = minmax_normalize(df['talk_ratio'])
    
    # 2) 점수 계산
    df['score'] = df.apply(
        lambda row: compute_stability_score_row(
            row['interruption_count_norm'], 
            row['silence_ratio_norm'],
            row['talk_ratio_norm']
        ),
        axis=1
    )
    
    # 3) 백분위 계산
    df['percentile'] = df['score'].rank(pct=True)
    
    # 4) 등급 부여
    df['grade'] = df['percentile'].apply(grade_from_percentile)

    if return_all:
        return df['score'].tolist(), df['grade'].tolist()
    else:
        return float(df['score'].iloc[0]), df['grade'].iloc[0]


# ===== 테스트용 코드 =====
if __name__ == "__main__":
    # robust하게 현재 파일 기준으로 경로 지정
    DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_data.csv')
    csv_df = pd.read_csv(DATA_PATH)
    # 필요한 컬럼만 추출하여 딕셔너리 리스트로 변환
    test_data = csv_df[['interruption_count', 'silence_ratio', 'talk_ratio']].to_dict('records')

    print(f"총 {len(test_data)}개 세션 데이터 로드 완료")
    print(f"첫 5개 세션 데이터 샘플:")
    for i, session in enumerate(test_data[:5]):
        print(f"  세션 {i+1}: 끊김={session['interruption_count']:.0f}회, 침묵={session['silence_ratio']:.3f}, 발화비율={session['talk_ratio']:.3f}")

    # 단일 세션 테스트
    score, grade = compute_stability_score_and_grade(test_data[:1])
    print(f"\n첫 번째 세션 - 점수: {score:.3f}, 등급: {grade}")

    # 전체 세션 테스트
    scores, grades = compute_stability_score_and_grade(test_data, return_all=True)
    print(f"\n전체 세션 결과:")
    print(f"점수 범위: {min(scores):.3f} ~ {max(scores):.3f}")
    print(f"등급 분포: {pd.Series(grades).value_counts().sort_index().to_dict()}")

    # 일부 세션 상세 결과 (상위 10개만)
    print(f"\n처음 10개 세션 상세 결과:")
    for i in range(min(10, len(scores))):
        print(f"세션 {i+1}: 점수 {scores[i]:.3f}, 등급 {grades[i]}")