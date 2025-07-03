import pandas as pd
import numpy as np
import os

def grade_from_score(score: float) -> str:
    if score == 1.0:
        return "A"
    elif score == 0.6:
        return "B"
    elif score == 0.2:
        return "C"
    elif score == 0.0:
        return "D"
    else:
        return "Invalid"

def compute_problem_solving_score_and_grade(
    data: list[dict],
    return_all: bool = False
):
    """
    문제 해결 역량 점수 및 등급 계산 함수.
    
    Note: suggestions 컬럼은 이미 정규화된 값 (0.0, 0.2, 0.6, 1.0)을 사용하므로
          추가 정규화 없이 그대로 점수로 사용합니다.

    Args:
        data: [{'suggestions': float}, ...]
        return_all: False면 첫 세션 결과, True면 모든 세션 리스트 반환.

    Returns:
        (score, grade) or (scores_list, grades_list)
    """
    df = pd.DataFrame(data)
    
    # 1) 유효성 검사: suggestions 값이 정해진 범위 내에 있는지 확인
    valid_scores = {0.0, 0.2, 0.6, 1.0}
    is_valid = df['suggestions'].isin(valid_scores)
    if not is_valid.all():
        invalid_rows = df[~is_valid]
        raise ValueError(f"유효하지 않은 점수가 발견되었습니다. 아래 데이터를 확인해주세요:\n{invalid_rows}")
    
    # 2) 점수 계산: suggestions 값을 그대로 사용 (이미 정규화됨)
    df['score'] = df['suggestions']
    
    # 3) 등급 부여
    df['grade'] = df['score'].apply(grade_from_score)

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
    test_data = csv_df[['suggestions']].to_dict('records')

    print(f"총 {len(test_data)}개 세션 데이터 로드 완료")
    print(f"첫 5개 세션 데이터 샘플:")
    for i, session in enumerate(test_data[:5]):
        print(f"  세션 {i+1}: 제안점수={session['suggestions']:.1f}")

    # 단일 세션 테스트
    score, grade = compute_problem_solving_score_and_grade(test_data[:1])
    print(f"\n첫 번째 세션 - 점수: {score:.3f}, 등급: {grade}")

    # 전체 세션 테스트
    scores, grades = compute_problem_solving_score_and_grade(test_data, return_all=True)
    print(f"\n전체 세션 결과:")
    print(f"점수 범위: {min(scores):.3f} ~ {max(scores):.3f}")
    print(f"등급 분포: {pd.Series(grades).value_counts().sort_index().to_dict()}")

    # 점수별 분포 확인
    print(f"\n점수별 분포:")
    score_dist = pd.Series(scores).value_counts().sort_index()
    for score_val, count in score_dist.items():
        print(f"  점수 {score_val:.1f}: {count}개 ({count/len(scores)*100:.1f}%)")

    # 일부 세션 상세 결과 (상위 10개만)
    print(f"\n처음 10개 세션 상세 결과:")
    for i in range(min(10, len(scores))):
        print(f"세션 {i+1}: 점수 {scores[i]:.3f}, 등급 {grades[i]}")