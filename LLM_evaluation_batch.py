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
당신은 상담사 교육 전문가입니다. 아래 5가지 핵심 지표별 평가 결과를 바탕으로 상담사의 성과를 체계적으로 분석하고 실용적인 코칭을 제공해 주세요.

📊 **평가 결과 분석**
1. **정중함 및 언어 품질** (점수: {evaluation_result['Politeness']['score']:.3f}, 등급: {evaluation_result['Politeness']['grade']})
   - 존댓말 사용률, 긍정적 언어 사용, 부정적 표현 최소화 등을 종합 평가
   - 등급 기준: A(상위10%), B(상위20%), C(상위30%), D(상위40%), E(상위50%), F(상위60%), G(하위40%)

2. **공감적 소통** (점수: {evaluation_result['Empathy']['score']:.3f}, 등급: {evaluation_result['Empathy']['grade']})
   - 고객 감정 이해 표현, 적절한 사과 및 위로의 말 사용 정도
   - 고객과의 정서적 연결 형성 능력 측정

3. **문제 해결 역량** (점수: {evaluation_result['ProblemSolving']['score']:.3f}, 등급: {evaluation_result['ProblemSolving']['grade']})
   - 고객 문제에 대한 구체적 해결책 제시 능력
   - 등급: A(완전해결), B(대부분해결), C(부분해결), D(해결방안미흡)

4. **감정 안정성** (점수: {evaluation_result['EmotionalStability']['score']:.3f}, 등급: {evaluation_result['EmotionalStability']['grade']})
   - 상담 과정에서 고객의 감정 상태 개선 정도
   - 고객 만족도와 직결되는 핵심 지표

5. **대화 흐름 및 응대 태도** (점수: {evaluation_result['Stability']['score']:.3f}, 등급: {evaluation_result['Stability']['grade']})
   - 대화 중단 최소화, 적절한 침묵 유지, 균형잡힌 대화 진행 능력

🎯 **상세 분석 요청**

**1. 핵심 강점 (상위 2-3개 지표 기준)**
- 각 강점이 고객 만족도에 미치는 구체적 영향
- 해당 강점을 더욱 발전시킬 수 있는 방안
- 다른 지표 개선에 활용할 수 있는 연결점

**2. 주요 개선 영역 (하위 2-3개 지표 기준)**
- 현재 등급의 의미와 개선 시 기대효과
- 개선이 시급한 이유 (고객 경험 관점)
- 단계별 개선 로드맵 제시

**3. 실행 가능한 코칭 전략**
- 즉시 적용 가능한 구체적 행동 방안 (3가지)
- 중장기 역량 개발 계획 (2가지)
- 성과 측정 및 피드백 방법

**4. 개선 우선순위**
- 가장 시급한 개선 영역 1순위 선정 및 근거
- 해당 영역 개선 시 전체 상담 품질에 미치는 파급효과

[출력 형식]
🌟 **핵심 강점**
- 
- 

⚠️ **주요 개선 영역**
- 
- 

💡 **실행 코칭 전략**
[즉시 실행]
1. 
2. 
3. 

[중장기 개발]
1. 
2. 

🎯 **개선 우선순위**
1순위: [영역명] - [구체적 근거와 기대효과]
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