import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import sys
from openai import OpenAI

# absolute_grading 모듈들 import
sys.path.append('./absolute_grading')
from grade_politeness_auto import get_politeness_results
from grade_empathy_auto import get_empathy_results
from grade_emotional_stability_auto import get_emotional_stability_results
from grade_stability_auto import get_stability_results
from grade_problem_solving import get_problem_solving_results

# .env 파일에서 환경변수 불러오기
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# 1. 데이터 로드 (new_data.csv 우선, 없으면 dummy_data.csv)
DATA_PATH = 'data/new_data.csv'
DUMMY_PATH = 'data/dummy_data.csv'

if os.path.exists(DATA_PATH):
    print(f"[INFO] new_data.csv로 평가를 진행합니다.")
    df = pd.read_csv(DATA_PATH)
else:
    print(f"[INFO] new_data.csv가 없어 dummy_data.csv로 평가를 진행합니다.")
    df = pd.read_csv(DUMMY_PATH)

df.columns = df.columns.str.strip()

# session_id가 없으면 자동 생성
def ensure_session_id(df):
    if 'session_id' not in df.columns:
        df = df.copy()
        df['session_id'] = [f'session_{i+1:03d}' for i in range(len(df))]
    return df

df = ensure_session_id(df)

# 2. 결과 저장 리스트
eval_results = []

# 3. OpenAI 모델 설정
MODEL_NAME = "gpt-4o-mini"

# 4. absolute_grading 시스템에서 평가 결과 가져오기
print("[INFO] absolute_grading 시스템에서 평가 결과를 가져오는 중...")

politeness_result = get_politeness_results()
empathy_result = get_empathy_results()
emotional_result = get_emotional_stability_results()
stability_result = get_stability_results()
problem_result = get_problem_solving_results()

print(f"[INFO] 평가 결과 로드 완료 - 총 {len(df)}개 세션")

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
            "score": float(problem_result['ProblemSolving_score'].iloc[idx]),
            "grade": problem_result['ProblemSolving_Grade'].iloc[idx]
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

    # OpenAI 프롬프트 생성
    prompt = f"""
당신은 상담사 교육 전문가입니다. 아래 5가지 지표 평가 결과를 바탕으로 간결하고 핵심적인 피드백을 제공해 주세요.

📊 **평가 결과**
- 정중함: {evaluation_result['Politeness']['score']:.3f}점 ({evaluation_result['Politeness']['grade']}등급)
- 공감: {evaluation_result['Empathy']['score']:.3f}점 ({evaluation_result['Empathy']['grade']}등급)  
- 문제해결: {evaluation_result['ProblemSolving']['score']:.3f}점 ({evaluation_result['ProblemSolving']['grade']}등급)
- 감정안정성: {evaluation_result['EmotionalStability']['score']:.3f}점 ({evaluation_result['EmotionalStability']['grade']}등급)
- 대화흐름: {evaluation_result['Stability']['score']:.3f}점 ({evaluation_result['Stability']['grade']}등급)

**출력 형식 (간결하게):**

** 강점 (상위 2개 지표)**
1. [지표명] (점수, 등급): 한 줄 설명
2. [지표명] (점수, 등급): 한 줄 설명

** 약점 (하위 2개 지표)**  
1. [지표명] (점수, 등급): 한 줄 설명
2. [지표명] (점수, 등급): 한 줄 설명

** 코칭 멘트**
강점과 약점을 활용한 3-4줄의 구체적이고 실행 가능한 개선 방안 제시
"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        feedback = response.choices[0].message.content
    except Exception as e:
        feedback = f"OpenAI API 호출 실패: {e}"

    eval_results.append({
        'session_id': session_id,
        'evaluation': evaluation_result,
        'feedback': feedback
    })
    print(f"[세션 {session_id}] 분석 완료!")

# 6. 전체 결과 출력
print(f"\n=== 전체 세션 분석 결과 (총 {len(eval_results)}개 세션) ===")
for r in eval_results:
    print(f"\n[세션 ID: {r['session_id']}]")
    print("📊 실제 평가 결과:")
    for key, value in r['evaluation'].items():
        print(f"  {key}: 점수 {value['score']:.3f}, 등급 {value['grade']}")
    print("-" * 40)
    print("🤖 OpenAI GPT 피드백:")
    print(r['feedback'])
    print("=" * 60) 