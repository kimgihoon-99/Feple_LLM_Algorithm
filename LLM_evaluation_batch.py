import os
from dotenv import load_dotenv
import requests
import json
import pandas as pd
import numpy as np
import sys
sys.path.append('./evaluation_algorithms')
from politeness import evaluate_politeness
from empathy import evaluate_empathy
from problem_solving import evaluate_problem_solving
from emotional_stability import evaluate_emotional_stability
from stability import evaluate_stability

# .env 파일에서 환경변수 불러오기
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 1. 더미 데이터 로드 (각 row가 하나의 상담 세션, session_id 컬럼 포함 가정)
df = pd.read_excel('data/dummy_data.xlsx')

# session_id가 없으면 자동 생성
def ensure_session_id(df):
    if 'session_id' not in df.columns:
        df = df.copy()
        df['session_id'] = [f'session_{i+1:03d}' for i in range(len(df))]
    return df

df = ensure_session_id(df)

# 2. 결과 저장 리스트
eval_results = []

# 3. 지원 모델 자동 선택 함수
def get_gemini_model():
    model_list_url = f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_API_KEY}"
    model_list_resp = requests.get(model_list_url)
    model_name = None
    if model_list_resp.status_code == 200:
        models = model_list_resp.json().get('models', [])
        preferred = ['gemini-1.5-pro', 'gemini-1.0-pro', 'gemini-pro', 'gemini-1.5-flash']
        for p in preferred:
            for m in models:
                if m['name'].endswith(p):
                    model_name = m['name'].split('/')[-1]
                    break
            if model_name:
                break
        if not model_name and models:
            model_name = models[0]['name'].split('/')[-1]
    else:
        raise Exception('모델 리스트 조회 실패')
    return model_name

model_name = get_gemini_model()
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent"
headers = {"Content-Type": "application/json"}

# 4. 전체 세션에 대해 평가지표별 일괄 평가
politeness_cols = ['honorific_ratio', 'positive_word_ratio', 'negative_word_ratio', 'euphonious_word_ratio']
empathy_cols = ['empathy_ratio', 'apology_ratio']
problem_cols = ['suggestions']
emotional_cols = ['customer_sentiment_early', 'customer_sentiment_late']
stability_cols = ['interruption_count', 'silence_ratio', 'talk_ratio']

politeness_df = df[politeness_cols].copy()
empathy_df = df[empathy_cols].copy()
problem_df = df[problem_cols].copy()
emotional_df = df[emotional_cols].copy()
stability_df = df[stability_cols].copy()

politeness_result = evaluate_politeness(politeness_df)
empathy_result = evaluate_empathy(empathy_df)
problem_result = evaluate_problem_solving(problem_df)
emotional_result = evaluate_emotional_stability(emotional_df)
stability_result = evaluate_stability(stability_df)

# 5. 각 세션별 반복 처리 (row별로 결과 추출)
for idx, row in df.iterrows():
    session_id = row['session_id']
    evaluation_result = {
        "Politeness": {
            "score": float(politeness_result['Politeness_score'].iloc[idx]),
            "grade": politeness_result['Politeness_Grade'].iloc[idx]
        },
        "Empathy": {
            "score": float(empathy_result['Empathy_score'].iloc[idx]),
            "grade": empathy_result['Empathy_Grade'].iloc[idx]
        },
        "ProblemSolving": {
            "score": float(problem_result['Problem_Solving_score'].iloc[idx]),
            "grade": problem_result['Problem_Solving_Grade'].iloc[idx]
        },
        "EmotionalStability": {
            "score": float(emotional_result['EmotionalStability_score'].iloc[idx]),
            "grade": emotional_result['EmotionalStability_Grade'].iloc[idx]
        },
        "Stability": {
            "score": float(stability_result['Stability_score'].iloc[idx]),
            "grade": stability_result['Stability_Grade'].iloc[idx]
        }
    }

    # Gemini 프롬프트 생성
    prompt = f"""
아래는 상담사의 5가지 평가 지표별 점수와 등급입니다. 각 항목을 참고하여 상담사의 강점, 약점, 그리고 구체적인 코칭 멘트를 작성해 주세요.

- 정중함 및 언어 품질 (Politeness): 점수 {evaluation_result['Politeness']['score']:.3f}, 등급 {evaluation_result['Politeness']['grade']}
- 공감적 소통 (Empathy): 점수 {evaluation_result['Empathy']['score']:.3f}, 등급 {evaluation_result['Empathy']['grade']}
- 문제 해결 역량 (Problem Solving): 점수 {evaluation_result['ProblemSolving']['score']:.3f}, 등급 {evaluation_result['ProblemSolving']['grade']}
- 감정 안정성 (Emotional Stability): 점수 {evaluation_result['EmotionalStability']['score']:.3f}, 등급 {evaluation_result['EmotionalStability']['grade']}
- 대화 흐름 및 응대 태도 (Stability): 점수 {evaluation_result['Stability']['score']:.3f}, 등급 {evaluation_result['Stability']['grade']}

[요청]
1. 상담사의 강점 2가지 이상
2. 상담사의 약점 2가지 이상
3. 상담사가 실제로 참고할 수 있는 구체적 코칭 멘트 2가지 이상

[출력 예시]
- 강점:
- 약점:
- 코칭 멘트:
"""
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(
        f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
        headers=headers,
        data=json.dumps(data)
    )
    if response.status_code == 200:
        result = response.json()
        try:
            feedback = result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            feedback = f"Gemini 응답 파싱 오류: {e}\n{result}"
    else:
        feedback = f"Gemini API 호출 실패: {response.status_code}\n{response.text}"

    eval_results.append({
        'session_id': session_id,
        'evaluation': evaluation_result,
        'feedback': feedback
    })
    print(f"[세션 {session_id}] 분석 완료!")

# 6. 전체 결과 출력
print("\n=== 전체 세션 분석 결과 ===")
for r in eval_results:
    print(f"\n[세션 ID: {r['session_id']}]")
    for key, value in r['evaluation'].items():
        print(f"{key}: 점수 {value['score']:.3f}, 등급 {value['grade']}")
    print("-" * 40)
    print(r['feedback'])
    print("=" * 60) 