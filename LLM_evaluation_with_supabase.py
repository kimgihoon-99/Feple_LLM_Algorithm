import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import sys
from openai import OpenAI
from supabase import create_client, Client
import json
from datetime import datetime
import time

# absolute_grading 모듈들 import
sys.path.append('./absolute_grading')
from grade_politeness_auto import get_politeness_results
from grade_empathy_auto import get_empathy_results
from grade_emotional_stability_auto import get_emotional_stability_results
from grade_stability_auto import get_stability_results
from grade_problem_solving import get_problem_solving_results

# === 각 지표별 metrics dict → 점수/등급 함수 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def minmax_normalize(value, min_val, max_val):
    if max_val > min_val:
        return (value - min_val) / (max_val - min_val)
    else:
        return 0.5

def compute_politeness_score_and_grade(metrics):
    path = os.path.join(BASE_DIR, 'cutoff', 'grade_cutoff_politeness.json')
    with open(path) as f:
        cutoff_json = json.load(f)
        cutoffs = cutoff_json['cutoff']
        minmax = cutoff_json['minmax']
    hr = minmax_normalize(metrics['honorific_ratio'], minmax['honorific_ratio']['min'], minmax['honorific_ratio']['max'])
    pr = minmax_normalize(metrics['positive_word_ratio'], minmax['positive_word_ratio']['min'], minmax['positive_word_ratio']['max'])
    er = minmax_normalize(metrics['euphonious_word_ratio'], minmax['euphonious_word_ratio']['min'], minmax['euphonious_word_ratio']['max'])
    nr = minmax_normalize(metrics['negative_word_ratio'], minmax['negative_word_ratio']['min'], minmax['negative_word_ratio']['max'])
    score = (hr + pr + er + (1 - nr)) / 4
    if score >= cutoffs["A"]: grade = "A"
    elif score >= cutoffs["B"]: grade = "B"
    elif score >= cutoffs["C"]: grade = "C"
    elif score >= cutoffs["D"]: grade = "D"
    elif score >= cutoffs["E"]: grade = "E"
    elif score >= cutoffs["F"]: grade = "F"
    else: grade = "G"
    return score, grade

def compute_empathy_score_and_grade(metrics):
    path = os.path.join(BASE_DIR, 'cutoff', 'grade_cutoff_empathy.json')
    with open(path) as f:
        cutoff_json = json.load(f)
        cutoffs = cutoff_json['cutoff']
        minmax = cutoff_json['minmax']
    er = minmax_normalize(metrics['empathy_ratio'], minmax['empathy_ratio']['min'], minmax['empathy_ratio']['max'])
    ar = minmax_normalize(metrics['apology_ratio'], minmax['apology_ratio']['min'], minmax['apology_ratio']['max'])
    score = er * 0.7 + ar * 0.3
    if score >= cutoffs["A"]: grade = "A"
    elif score >= cutoffs["B"]: grade = "B"
    elif score >= cutoffs["C"]: grade = "C"
    elif score >= cutoffs["D"]: grade = "D"
    elif score >= cutoffs["E"]: grade = "E"
    elif score >= cutoffs["F"]: grade = "F"
    else: grade = "G"
    return score, grade

def compute_problem_solving_score_and_grade(metrics):
    # 문제해결은 이산형 점수 매핑
    score = float(metrics['suggestions'])
    if score == 1.0:
        grade = "A"
    elif score == 0.6:
        grade = "B"
    elif score == 0.2:
        grade = "C"
    elif score == 0.0:
        grade = "D"
    else:
        grade = "Invalid"
    return score, grade

def compute_emotional_stability_score_and_grade(metrics):
    path = os.path.join(BASE_DIR, 'cutoff', 'grade_cutoff_emotional_stability.json')
    with open(path) as f:
        cutoff_json = json.load(f)
        cutoffs = cutoff_json['cutoff']
        minmax = cutoff_json['minmax']
    early = minmax_normalize(metrics['customer_sentiment_early'], minmax['customer_sentiment_early']['min'], minmax['customer_sentiment_early']['max'])
    late = minmax_normalize(metrics['customer_sentiment_late'], minmax['customer_sentiment_late']['min'], minmax['customer_sentiment_late']['max'])
    change = late - early
    if change == 0:
        if early < 0.4:
            raw = 0.50
        elif early >= 0.7:
            raw = 0.95
        else:
            raw = 0.85
    else:
        improvement = max(change, 0.0)
        raw = late * 0.7 + improvement * 0.3
    score = max(0.0, min(raw, 1.0))
    if score >= cutoffs["A"]: grade = "A"
    elif score >= cutoffs["B"]: grade = "B"
    elif score >= cutoffs["C"]: grade = "C"
    elif score >= cutoffs["D"]: grade = "D"
    elif score >= cutoffs["E"]: grade = "E"
    elif score >= cutoffs["F"]: grade = "F"
    else: grade = "G"
    return score, grade

def compute_stability_score_and_grade(metrics):
    path = os.path.join(BASE_DIR, 'cutoff', 'grade_cutoff_stability.json')
    with open(path) as f:
        cutoff_json = json.load(f)
        cutoffs = cutoff_json['cutoff']
        minmax = cutoff_json['minmax']
    ic = minmax_normalize(metrics['interruption_count'], minmax['interruption_count']['min'], minmax['interruption_count']['max'])
    sr = minmax_normalize(metrics['silence_ratio'], minmax['silence_ratio']['min'], minmax['silence_ratio']['max'])
    tr = minmax_normalize(metrics['talk_ratio'], minmax['talk_ratio']['min'], minmax['talk_ratio']['max'])
    interrupt_score = 1 - ic
    optimal_silence = 0.25
    silence_distance = abs(sr - optimal_silence)
    silence_score = max(0.0, 1 - 4 * silence_distance)
    talk_distance = abs(tr - 0.5)
    talk_score = max(0.0, 1 - 2 * talk_distance)
    score = interrupt_score * 0.3 + silence_score * 0.4 + talk_score * 0.3
    score = float(np.clip(score, 0.0, 1.0))
    if score >= cutoffs["A"]: grade = "A"
    elif score >= cutoffs["B"]: grade = "B"
    elif score >= cutoffs["C"]: grade = "C"
    elif score >= cutoffs["D"]: grade = "D"
    elif score >= cutoffs["E"]: grade = "E"
    elif score >= cutoffs["F"]: grade = "F"
    else: grade = "G"
    return score, grade

# === metrics dict → 5대 지표 점수/등급 dict ===
def metrics_to_scores_and_grades(metrics):
    politeness_score, politeness_grade = compute_politeness_score_and_grade(metrics)
    empathy_score, empathy_grade = compute_empathy_score_and_grade(metrics)
    problem_score, problem_grade = compute_problem_solving_score_and_grade(metrics)
    emotional_score, emotional_grade = compute_emotional_stability_score_and_grade(metrics)
    stability_score, stability_grade = compute_stability_score_and_grade(metrics)
    return {
        "Politeness": {"score": politeness_score, "grade": politeness_grade},
        "Empathy": {"score": empathy_score, "grade": empathy_grade},
        "ProblemSolving": {"score": problem_score, "grade": problem_grade},
        "EmotionalStability": {"score": emotional_score, "grade": emotional_grade},
        "Stability": {"score": stability_score, "grade": stability_grade}
    }

# .env 파일에서 환경변수 불러오기
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 클라이언트 초기화
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Supabase 클라이언트 초기화
def init_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[WARNING] Supabase 연결 정보가 없습니다. 결과는 로컬에만 출력됩니다.")
        return None
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[INFO] Supabase 연결 성공!")
        return supabase
    except Exception as e:
        print(f"[ERROR] Supabase 연결 실패: {e}")
        return None

supabase = init_supabase()

# Supabase에서 analysis_results 테이블의 미처리 row를 polling하여 가져오는 함수

def get_unprocessed_analysis_results():
    if not supabase:
        print("[ERROR] Supabase 연결이 필요합니다.")
        return []
    # 이미 평가된 session_id 목록 가져오기
    evaluated = supabase.table("counselor_evaluations").select("session_id").execute().data
    evaluated_ids = set(row["session_id"] for row in evaluated)
    # analysis_results에서 평가 안된 row만 가져오기
    analysis_rows = supabase.table("analysis_results").select("*").execute().data
    return [row for row in analysis_rows if row["session_id"] not in evaluated_ids]

# 1. 데이터 로드 (new_data.csv 우선, 없으면 dummy_data.csv)
DATA_PATH = 'data/new_data.csv'
DUMMY_PATH = 'data/dummy_data.csv'

if os.path.exists(DATA_PATH):
    print(f"[INFO] new_data.csv로 평가를 진행합니다.")
    df = pd.read_csv(DATA_PATH)
    data_source = "new_data.csv"
else:
    print(f"[INFO] new_data.csv가 없어 dummy_data.csv로 평가를 진행합니다.")
    df = pd.read_csv(DUMMY_PATH)
    data_source = "dummy_data.csv"

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

# === 새 자동화 파이프라인 함수들 ===

def run_llm_evaluation_with_scores(scores, transcript):
    prompt = f"""
    상담사 5대지표 평가 결과:
    - 정중함: {scores['Politeness']['score']:.3f}점 ({scores['Politeness']['grade']}등급)
    - 공감: {scores['Empathy']['score']:.3f}점 ({scores['Empathy']['grade']}등급)
    - 문제해결: {scores['ProblemSolving']['score']:.3f}점 ({scores['ProblemSolving']['grade']}등급)
    - 감정안정성: {scores['EmotionalStability']['score']:.3f}점 ({scores['EmotionalStability']['grade']}등급)
    - 대화흐름: {scores['Stability']['score']:.3f}점 ({scores['Stability']['grade']}등급)

    대화: {transcript}

    강점(상위 2개 지표), 약점(하위 2개 지표), 코칭멘트를 간결하게 작성해 주세요.
    """
    try:
        response = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        feedback = response.choices[0].message.content
    except Exception as e:
        feedback = f"OpenAI API 호출 실패: {e}"
    return feedback

def save_analysis_feedback_to_supabase(row, scores, feedback):
    if not supabase:
        return False
    try:
        data = {
            "session_id": row["session_id"],
            "politeness_score": scores["Politeness"]["score"],
            "politeness_grade": scores["Politeness"]["grade"],
            "empathy_score": scores["Empathy"]["score"],
            "empathy_grade": scores["Empathy"]["grade"],
            "problem_solving_score": scores["ProblemSolving"]["score"],
            "problem_solving_grade": scores["ProblemSolving"]["grade"],
            "emotional_stability_score": scores["EmotionalStability"]["score"],
            "emotional_stability_grade": scores["EmotionalStability"]["grade"],
            "stability_score": scores["Stability"]["score"],
            "stability_grade": scores["Stability"]["grade"],
            "gpt_feedback": feedback,
            "evaluation_model": MODEL_NAME,
            "data_source": "analysis_results"
        }
        result = supabase.table('counselor_evaluations').insert(data).execute()
        if result.data:
            print(f"[SUPABASE] 세션 {row['session_id']} 데이터 저장 성공!")
            return True
        else:
            print(f"[SUPABASE] 세션 {row['session_id']} 데이터 저장 실패")
            return False
    except Exception as e:
        print(f"[SUPABASE ERROR] 세션 {row['session_id']} 저장 중 오류: {e}")
        return False

def main():
    print("[자동화] Supabase analysis_results → 산식 점수/등급 → LLM 평가 → counselor_evaluations 저장 파이프라인 시작!")
    while True:
        unprocessed_rows = get_unprocessed_analysis_results()
        print(f"[자동화] 처리할 row 개수: {len(unprocessed_rows)}")
        for row in unprocessed_rows:
            metrics = row.get("metrics")
            transcript = row.get("transcript")
            scores = metrics_to_scores_and_grades(metrics)
            feedback = run_llm_evaluation_with_scores(scores, transcript)
            save_analysis_feedback_to_supabase(row, scores, feedback)
            print(f"[자동화] session_id {row['session_id']} 처리 완료")
        time.sleep(10)

if __name__ == "__main__":
    main()

# 6. 각 세션별 반복 처리 (row별로 결과 추출)
# for idx, row in df.iterrows():
#     session_id = row['session_id']
#     evaluation_result = {
#         "Politeness": {
#             "score": float(politeness_result['Politeness_score'].iloc[idx]),
#             "grade": politeness_result['Politeness_Grade'].iloc[idx]
#         },
#         "Empathy": {
#             "score": float(empathy_result['Empathy_score'].iloc[idx]),
#             "grade": empathy_result['Empathy_Grade'].iloc[idx]
#         },
#         "ProblemSolving": {
#             "score": float(problem_result['ProblemSolving_score'].iloc[idx]),
#             "grade": problem_result['ProblemSolving_Grade'].iloc[idx]
#         },
#         "EmotionalStability": {
#             "score": float(emotional_result['EmotionalStability_score'].iloc[idx]),
#             "grade": emotional_result['EmotionalStability_Grade'].iloc[idx]
#         },
#         "Stability": {
#             "score": float(stability_result['Stability_score'].iloc[idx]),
#             "grade": stability_result['Stability_Grade'].iloc[idx]
#         }
#     }

#     # OpenAI 프롬프트 생성
#     prompt = f"""
# 당신은 상담사 교육 전문가입니다. 아래 5가지 지표 평가 결과를 바탕으로 간결하고 핵심적인 피드백을 제공해 주세요.

# 📊 **평가 결과**
# - 정중함: {evaluation_result['Politeness']['score']:.3f}점 ({evaluation_result['Politeness']['grade']}등급)
# - 공감: {evaluation_result['Empathy']['score']:.3f}점 ({evaluation_result['Empathy']['grade']}등급)  
# - 문제해결: {evaluation_result['ProblemSolving']['score']:.3f}점 ({evaluation_result['ProblemSolving']['grade']}등급)
# - 감정안정성: {evaluation_result['EmotionalStability']['score']:.3f}점 ({evaluation_result['EmotionalStability']['grade']}등급)
# - 대화흐름: {evaluation_result['Stability']['score']:.3f}점 ({evaluation_result['Stability']['grade']}등급)

# **출력 형식 (간결하게):**

# ** 강점 (상위 2개 지표)**
# 1. [지표명] (점수, 등급): 한 줄 설명
# 2. [지표명] (점수, 등급): 한 줄 설명

# ** 약점 (하위 2개 지표)**  
# 1. [지표명] (점수, 등급): 한 줄 설명
# 2. [지표명] (점수, 등급): 한 줄 설명

# ** 코칭 멘트**
# 강점과 약점을 활용한 3-4줄의 구체적이고 실행 가능한 개선 방안 제시
# """
#     try:
#         response = openai_client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=1500,
#             temperature=0.7
#         )
#         feedback = response.choices[0].message.content
#     except Exception as e:
#         feedback = f"OpenAI API 호출 실패: {e}"

#     # Supabase에 저장
#     save_success = save_to_supabase(session_id, evaluation_result, feedback, data_source)
    
#     eval_results.append({
#         'session_id': session_id,
#         'evaluation': evaluation_result,
#         'feedback': feedback,
#         'saved_to_supabase': save_success
#     })
#     print(f"[세션 {session_id}] 분석 완료! {'(Supabase 저장 성공)' if save_success else '(로컬만 저장)'}")

# 7. 전체 결과 출력
# print(f"\n=== 전체 세션 분석 결과 (총 {len(eval_results)}개 세션) ===")
# saved_count = sum(1 for r in eval_results if r.get('saved_to_supabase', False))
# print(f"📊 Supabase 저장: {saved_count}/{len(eval_results)}개 세션 성공")

# for r in eval_results:
#     print(f"\n[세션 ID: {r['session_id']}]")
#     print("📊 실제 평가 결과:")
#     for key, value in r['evaluation'].items():
#         print(f"  {key}: 점수 {value['score']:.3f}, 등급 {value['grade']}")
#     print("-" * 40)
#     print("🤖 OpenAI GPT 피드백:")
#     print(r['feedback'])
#     if r.get('saved_to_supabase'):
#         print("✅ Supabase에 저장 완료")
#     else:
#         print("❌ Supabase 저장 실패")
#     print("=" * 60)

# 8. 저장된 데이터 요약 정보
# if supabase and saved_count > 0:
#     print(f"\n🎯 **Supabase 저장 완료!**")
#     print(f"- 테이블: counselor_evaluations")
#     print(f"- 저장된 세션: {saved_count}개")
#     print(f"- 데이터 소스: {data_source}")
#     print(f"- 평가 모델: {MODEL_NAME}")
#     print(f"- 저장 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 