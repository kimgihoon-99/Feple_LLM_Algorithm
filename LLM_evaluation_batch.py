import os
from dotenv import load_dotenv
import requests
import json
import pandas as pd
import numpy as np
import sys

# .env 파일에서 환경변수 불러오기
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 1. new_data.csv 로드
DATA_PATH = os.path.join('data', 'new_data.csv')
df = pd.read_csv(DATA_PATH)

# 2. 각 지표별 평가 함수 import (외부 호출 evaluate_XXX 함수 사용)
from absolute_grading.grade_politeness_auto import evaluate_politeness
from absolute_grading.grade_empathy_auto import evaluate_empathy
from absolute_grading.grade_problem_solving import evaluate_problem_solving
from absolute_grading.grade_emotional_stability_auto import evaluate_emotional_stability
from absolute_grading.grade_stability_auto import evaluate_stability

# 3. 점수/등급 산출 (여기서는 첫 번째 row만 예시)
session_id = df['session_id'].iloc[0] if 'session_id' in df.columns else 'unknown_session'
politeness_result = evaluate_politeness(df)
empathy_result = evaluate_empathy(df)
problem_solving_result = evaluate_problem_solving(df)
emotional_stability_result = evaluate_emotional_stability(df)
stability_result = evaluate_stability(df)

evaluation_result = {
    "Politeness": {
        "score": politeness_result['Politeness_score'].iloc[0],
        "grade": politeness_result['Politeness_Grade'].iloc[0]
    },
    "Empathy": {
        "score": empathy_result['Empathy_score'].iloc[0],
        "grade": empathy_result['Empathy_Grade'].iloc[0]
    },
    "ProblemSolving": {
        "score": problem_solving_result['ProblemSolving_score'].iloc[0],
        "grade": problem_solving_result['ProblemSolving_Grade'].iloc[0]
    },
    "EmotionalStability": {
        "score": emotional_stability_result['EmotionalStability_score'].iloc[0],
        "grade": emotional_stability_result['EmotionalStability_Grade'].iloc[0]
    },
    "Stability": {
        "score": stability_result['Stability_score'].iloc[0],
        "grade": stability_result['Stability_Grade'].iloc[0]
    }
}

# Gemini 지원 모델 자동 선택 함수
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

# 4. Gemini 프롬프트 생성
def make_gemini_prompt(evaluation_result, session_id):
    prompt = (
        f"아래는 상담사의 5가지 평가 지표별 점수와 등급입니다. "
        "각 항목을 참고하여 상담사의 강점, 약점, 그리고 구체적인 개선점 및 코칭 멘트를 작성해 주세요.\n\n"
        f"- 정중함 및 언어 품질 (Politeness): 점수 {evaluation_result['Politeness']['score']:.2f}, 등급 {evaluation_result['Politeness']['grade']}\n"
        f"- 공감적 소통 (Empathy): 점수 {evaluation_result['Empathy']['score']:.2f}, 등급 {evaluation_result['Empathy']['grade']}\n"
        f"- 문제 해결 역량 (Problem Solving): 점수 {evaluation_result['ProblemSolving']['score']:.2f}, 등급 {evaluation_result['ProblemSolving']['grade']}\n"
        f"- 감정 안정성 (Emotional Stability): 점수 {evaluation_result['EmotionalStability']['score']:.2f}, 등급 {evaluation_result['EmotionalStability']['grade']}\n"
        f"- 대화 흐름 및 응대 태도 (Stability): 점수 {evaluation_result['Stability']['score']:.2f}, 등급 {evaluation_result['Stability']['grade']}\n\n"
        "[요청]\n"
        "1. 상담사의 강점 2가지 이상\n"
        "2. 상담사의 약점 2가지 이상\n"
        "3. 상담사가 실제로 참고할 수 있는 구체적 개선점/코칭 멘트 2가지 이상\n\n"
        "[출력 형식]\n"
        f"## 상담사 평가 분석 (세션 ID: {session_id})\n"
        "- 강점:\n"
        "  - 예시1\n"
        "  - 예시2\n"
        "- 약점:\n"
        "  - 예시1\n"
        "  - 예시2\n"
        "- 개선점/코칭 멘트:\n"
        "  - 예시1\n"
        "  - 예시2\n"
    )
    return prompt

# 5. Gemini API 호출
headers = {"Content-Type": "application/json"}
data = {
    "contents": [
        {"parts": [{"text": make_gemini_prompt(evaluation_result, session_id)}]}
    ]
}

response = requests.post(
    f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
    headers=headers,
    json=data
)

if response.status_code == 200:
    result = response.json()
    print(result['candidates'][0]['content']['parts'][0]['text'])
else:
    print("Gemini API 호출 실패:", response.status_code)
    print(response.text) 