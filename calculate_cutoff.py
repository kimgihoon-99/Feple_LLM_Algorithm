import pandas as pd
import numpy as np
import json
import os
from legacy.evaluation_algorithms.politeness import evaluate_politeness
from legacy.evaluation_algorithms.empathy import evaluate_empathy
from legacy.evaluation_algorithms.problem_solving import compute_problem_solving_score_and_grade
from legacy.evaluation_algorithms.emotional_stability import evaluate_emotional_stability
from legacy.evaluation_algorithms.stability import compute_stability_score_and_grade

# robust하게 현재 파일 기준으로 데이터 경로 지정
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'dummy_data.csv')
df = pd.read_csv(DATA_PATH)

# 각 평가지표별 점수 산출
politeness_scores = evaluate_politeness(df[['honorific_ratio', 'positive_word_ratio', 'negative_word_ratio', 'euphonious_word_ratio']])['Politeness_score'].tolist()
empathy_scores = evaluate_empathy(df[['empathy_ratio', 'apology_ratio']])['Empathy_score'].tolist()
problem_solving_scores, _ = compute_problem_solving_score_and_grade(df[['suggestions']].to_dict(orient='records'), return_all=True)
emotional_stability_scores = evaluate_emotional_stability(df[['customer_sentiment_early', 'customer_sentiment_late']])['EmotionalStability_score'].tolist()
stability_scores, _ = compute_stability_score_and_grade(df[['interruption_count', 'silence_ratio', 'talk_ratio']].to_dict(orient='records'), return_all=True)

scores_dict = {
    'politeness': politeness_scores,
    'empathy': empathy_scores,
    'problem_solving': problem_solving_scores,
    'emotional_stability': emotional_stability_scores,
    'stability': stability_scores,
}

# 3. cut-off 산출 함수
def get_cutoffs(scores, key=None):
    if key == 'problem_solving':
        # 이산형 점수에 대한 절대 등급 매핑
        return {
            "A": 1.0,
            "B": 0.6,
            "C": 0.2,
            "D": 0.0
        }
    else:
        return {
            "A": float(np.percentile(scores, 90)),
            "B":  float(np.percentile(scores, 80)),
            "C": float(np.percentile(scores, 70)),
            "D":  float(np.percentile(scores, 60)),
            "E": float(np.percentile(scores, 50)),
            "F":  float(np.percentile(scores, 40)),
            "G":  -1e9
        }

def get_minmax(df, cols):
    return {col: {"min": float(df[col].min()), "max": float(df[col].max())} for col in cols}

# 4. cut-off 폴더 생성 (없으면)
CUTOFF_DIR = os.path.join(os.path.dirname(__file__), 'cutoff')
os.makedirs(CUTOFF_DIR, exist_ok=True)

# 5. 각 지표별 cut-off 산출 및 저장
for key, scores in scores_dict.items():
    cutoffs = get_cutoffs(scores, key)
    # feature별 minmax 계산 (problem_solving은 제외)
    if key == 'politeness':
        minmax = get_minmax(df, ['honorific_ratio', 'positive_word_ratio', 'negative_word_ratio', 'euphonious_word_ratio'])
    elif key == 'empathy':
        minmax = get_minmax(df, ['empathy_ratio', 'apology_ratio'])
    elif key == 'emotional_stability':
        minmax = get_minmax(df, ['customer_sentiment_early', 'customer_sentiment_late'])
    elif key == 'stability':
        minmax = get_minmax(df, ['interruption_count', 'silence_ratio', 'talk_ratio'])
    else:
        minmax = None
    filename = os.path.join(CUTOFF_DIR, f'grade_cutoff_{key}.json')
    if minmax is not None:
        with open(filename, 'w') as f:
            json.dump({'cutoff': cutoffs, 'minmax': minmax}, f, indent=2)
    else:
        with open(filename, 'w') as f:
            json.dump(cutoffs, f, indent=2)
    print(f"{key} cut-off saved to {filename}: {cutoffs}")