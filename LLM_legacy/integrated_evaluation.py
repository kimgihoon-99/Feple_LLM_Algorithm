import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from openai import OpenAI

# 5가지 평가지표 알고리즘 import
import sys
sys.path.append('./evaluation_algorithms')
from politeness import evaluate_politeness
from empathy import evaluate_empathy
from problem_solving import evaluate_problem_solving
from emotional_stability import evaluate_emotional_stability
from stability import evaluate_stability

# .env 파일에서 환경변수 불러오기
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def run_integrated_evaluation():
    print("=== 5가지 상담사 평가지표 통합 평가 시스템 ===")
    
    # 1. 예시 데이터 생성 (실제로는 1차 DB에서 가져온 데이터)
    print("\n[1단계] 예시 데이터 생성...")
    
    # Politeness 데이터
    politeness_data = [
        {'honorific_ratio': 85.5, 'positive_word_ratio': 12.3, 'negative_word_ratio': 2.1, 'euphonious_word_ratio': 8.7},
        {'honorific_ratio': 45.2, 'positive_word_ratio': 8.1, 'negative_word_ratio': 15.3, 'euphonious_word_ratio': 3.2},
        {'honorific_ratio': 92.1, 'positive_word_ratio': 18.7, 'negative_word_ratio': 1.2, 'euphonious_word_ratio': 12.4}
    ]
    
    # Empathy 데이터
    empathy_data = [
        {'empathy_ratio': 15.2, 'apology_ratio': 3.4},
        {'empathy_ratio': 8.7, 'apology_ratio': 1.2},
        {'empathy_ratio': 22.1, 'apology_ratio': 5.8}
    ]
    
    # Problem Solving 데이터
    problem_solving_data = [
        {'suggestions': 1.0},
        {'suggestions': 0.2},
        {'suggestions': 0.6}
    ]
    
    # Emotional Stability 데이터
    emotional_stability_data = [
        {'customer_sentiment_early': 0.2, 'customer_sentiment_late': 0.8},
        {'customer_sentiment_early': 0.8, 'customer_sentiment_late': 0.8},
        {'customer_sentiment_early': 0.3, 'customer_sentiment_late': 0.3}
    ]
    
    # Stability 데이터
    stability_data = [
        {'interruption_count': 0, 'silence_ratio': 0.07, 'talk_ratio': 0.75},
        {'interruption_count': 3, 'silence_ratio': 0.25, 'talk_ratio': 0.35},
        {'interruption_count': 1, 'silence_ratio': 0.12, 'talk_ratio': 0.65}
    ]
    
    # 2. 각 평가지표 알고리즘 실행
    print("\n[2단계] 5가지 평가지표 알고리즘 실행...")
    
    # Politeness 평가
    politeness_df = pd.DataFrame(politeness_data)
    politeness_result = evaluate_politeness(politeness_df)
    politeness_score = politeness_result['Politeness_score'].iloc[0]  # 첫 번째 상담사 결과
    politeness_grade = politeness_result['Politeness_Grade'].iloc[0]
    
    # Empathy 평가
    empathy_df = pd.DataFrame(empathy_data)
    empathy_result = evaluate_empathy(empathy_df)
    empathy_score = empathy_result['Empathy_score'].iloc[0]
    empathy_grade = empathy_result['Empathy_Grade'].iloc[0]
    
    # Problem Solving 평가
    problem_solving_df = pd.DataFrame(problem_solving_data)
    problem_solving_result = evaluate_problem_solving(problem_solving_df)
    problem_solving_score = problem_solving_result['Problem_Solving_score'].iloc[0]
    problem_solving_grade = problem_solving_result['Problem_Solving_Grade'].iloc[0]
    
    # Emotional Stability 평가
    emotional_stability_df = pd.DataFrame(emotional_stability_data)
    emotional_stability_result = evaluate_emotional_stability(emotional_stability_df)
    emotional_stability_score = emotional_stability_result['EmotionalStability_score'].iloc[0]
    emotional_stability_grade = emotional_stability_result['EmotionalStability_Grade'].iloc[0]
    
    # Stability 평가
    stability_df = pd.DataFrame(stability_data)
    stability_result = evaluate_stability(stability_df)
    stability_score = stability_result['Stability_score'].iloc[0]
    stability_grade = stability_result['Stability_Grade'].iloc[0]
    
    # 3. 실제 산출된 점수와 등급을 Gemini API용 형식으로 정리
    print("\n[3단계] 실제 산출된 점수 및 등급 정리...")
    evaluation_result = {
        "Politeness": {"score": politeness_score, "grade": politeness_grade},
        "Empathy": {"score": empathy_score, "grade": empathy_grade},
        "ProblemSolving": {"score": problem_solving_score, "grade": problem_solving_grade},
        "EmotionalStability": {"score": emotional_stability_score, "grade": emotional_stability_grade},
        "Stability": {"score": stability_score, "grade": stability_grade}
    }
    
    print("실제 산출된 평가 결과:")
    for key, value in evaluation_result.items():
        print(f"  {key}: 점수 {value['score']:.3f}, 등급 {value['grade']}")
    
    # 4. Gemini API에 전달할 프롬프트 생성
    print("\n[4단계] Gemini API 프롬프트 생성...")
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
    
    # 5. OpenAI API 호출
    print("\n[5단계] OpenAI API 호출...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        feedback = response.choices[0].message.content
        api_success = True
    except Exception as e:
        print(f"OpenAI API 호출 실패: {e}")
        feedback = f"API 호출 실패: {e}"
        api_success = False
    
    # 6. 결과 출력
    print("\n[6단계] 최종 결과 출력...")
    print("=" * 60)
    
    if api_success:
        print("[실제 산출된 평가 지표별 점수 및 등급]")
        print("-" * 50)
        for key, value in evaluation_result.items():
            print(f"{key}: 점수 {value['score']:.3f}, 등급 {value['grade']}")
        print("-" * 50)
        
        print("[OpenAI GPT 상담사 피드백 결과]")
        print(feedback)
    else:
        print("OpenAI API 호출 실패")
        print(feedback)
    
    print("=" * 60)
    print("통합 평가 완료!")

if __name__ == "__main__":
    run_integrated_evaluation() 