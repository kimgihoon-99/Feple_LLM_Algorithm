import pandas as pd
import os
import sys

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'new_data.csv')
DUMMY_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_data.csv')
if os.path.exists(DATA_PATH):
    print(f"[INFO] new_data.csv로 평가를 진행합니다.")
    eval_path = DATA_PATH
else:
    print(f"[INFO] new_data.csv가 없어 dummy_data.csv로 평가를 진행합니다.")
    eval_path = DUMMY_PATH

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

# 1. 데이터 로드
df = pd.read_csv(eval_path)

# 2. 점수 및 등급 부여
valid_scores = {0.0, 0.2, 0.6, 1.0}
if not set(df['suggestions']).issubset(valid_scores):
    raise ValueError("유효하지 않은 점수 발견")
df['ProblemSolving_Grade'] = df['suggestions'].apply(grade_from_score)

print(df[['suggestions', 'ProblemSolving_Grade']].head(20))

def evaluate_problem_solving(df):
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
    valid_scores = {0.0, 0.2, 0.6, 1.0}
    if not set(df['suggestions']).issubset(valid_scores):
        raise ValueError("유효하지 않은 점수 발견")
    df = df.copy()
    df['ProblemSolving_score'] = df['suggestions']
    df['ProblemSolving_Grade'] = df['suggestions'].apply(grade_from_score)
    return df[['ProblemSolving_score', 'ProblemSolving_Grade']] 