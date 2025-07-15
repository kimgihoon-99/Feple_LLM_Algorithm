# 상담사 5대 지표 LLM 평가 시스템

## 프로젝트 개요

이 프로젝트는 상담사 평가를 위해 **실제 평가 알고리즘**을 통해 5대 핵심 지표(정중함, 공감, 문제해결, 감정안정성, 대화흐름)를 정확하게 산출하고, **OpenAI GPT API**를 활용한 전문적인 피드백(강점/약점/코칭멘트)을 자동 생성하는 실전형 평가 파이프라인입니다.

### 🎯 핵심 특징
- **실제 평가 시스템 연동**: absolute_grading 알고리즘에서 산출한 정확한 점수/등급 사용
- **OpenAI GPT 기반**: 전문가 역할로 설정된 상담사 교육 전문가로 설정
- **자동화된 평가 파이프라인**: 데이터 입력부터 피드백 생성까지 완전 자동화
- **백분위 기반 절대평가**: A~G 등급 체계로 객관적 성과 측정
- **실시간 기준선 갱신**: 신규 데이터 범위 초과 시 자동 cutoff/minmax 재산출

---

## 디렉토리 구조

```
Feple_LLM_Algorithm/
│
├── absolute_grading/         # 🎯 실제 평가 알고리즘 (메인 시스템)
│   ├── grade_politeness_auto.py      # 정중함 평가
│   ├── grade_empathy_auto.py         # 공감 평가
│   ├── grade_emotional_stability_auto.py # 감정안정성 평가
│   ├── grade_stability_auto.py       # 대화흐름 평가
│   └── grade_problem_solving.py      # 문제해결 평가
│
├── legacy/                   # 구버전 평가 스크립트 및 알고리즘
│   ├── evaluation_algorithms/    # 구버전 평가 알고리즘
│   │   ├── politeness.py
│   │   ├── empathy.py
│   │   ├── problem_solving.py
│   │   ├── emotional_stability.py
│   │   └── stability.py
│   ├── grade_politeness.py
│   ├── grade_empathy.py
│   ├── grade_emotional_stability.py
│   └── grade_stability.py
│
├── data/                     # 평가용 데이터
│   ├── dummy_data.csv        # 기준선 산출용(기존) 데이터
│   └── new_data.csv          # 신규 평가 데이터 (없으면 dummy_data로 평가)
│
├── cutoff/                   # 각 지표별 cut-off 및 minmax 기준선(json)
│   ├── grade_cutoff_politeness.json
│   ├── grade_cutoff_empathy.json
│   ├── grade_cutoff_emotional_stability.json
│   ├── grade_cutoff_stability.json
│   └── grade_cutoff_problem_solving.json
│
├── calculate_cutoff.py       # cut-off 및 minmax 기준선 산출/갱신 스크립트
├── batch_grade_all.py        # 5개 평가 스크립트 일괄 실행 배치
├── integrated_evaluation.py  # 5대 지표 통합 평가 및 OpenAI 피드백 생성
├── integrated_evaluation_batch.py # (확장) 통합 평가 배치 스크립트
├── LLM_evaluation_batch.py   # 🚀 메인 실행 파일: 실제 평가시스템 + OpenAI 피드백
└── README.md                 # 프로젝트 문서
```

---

## 🚀 메인 실행 방법

### 1. 환경 설정
```bash
# OpenAI API 키 설정 (.env 파일 생성)
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 2. 메인 실행 (권장)
```bash
python LLM_evaluation_batch.py
```

**🎯 이 파일이 모든 것을 처리합니다:**
- ✅ 데이터 로드 (new_data.csv 우선, 없으면 dummy_data.csv)
- ✅ 5대 지표별 실제 평가 알고리즘 실행
- ✅ 정확한 점수/등급 산출
- ✅ OpenAI GPT를 통한 전문적 피드백 생성
- ✅ 체계적인 결과 출력 (강점/약점/코칭전략/우선순위)

### 3. 개별 실행 (선택사항)

#### 3-1. cut-off 및 minmax 기준선 산출
```bash
python calculate_cutoff.py
```

#### 3-2. 평가 알고리즘만 실행
```bash
python batch_grade_all.py
```

#### 3-3. 구버전 통합 평가
```bash
python integrated_evaluation.py
```

---

## 🎯 5대 평가 지표

### 1. 📝 정중함 및 언어 품질 (Politeness)
- **측정 요소**: 존댓말 사용률, 긍정적 언어 사용, 부정적 표현 최소화
- **계산 공식**: `(honorific_ratio + positive_word_ratio + euphonious_word_ratio + (1-negative_word_ratio)) / 4`
- **등급 체계**: A~G (7단계, 백분위 기반)

### 2. 🤝 공감적 소통 (Empathy)
- **측정 요소**: 고객 감정 이해 표현, 적절한 사과 및 위로
- **계산 공식**: `empathy_ratio * 0.7 + apology_ratio * 0.3`
- **등급 체계**: A~G (7단계, 백분위 기반)

### 3. 💡 문제 해결 역량 (Problem Solving)
- **측정 요소**: 고객 문제에 대한 구체적 해결책 제시
- **계산 방식**: 이산형 점수 매핑
- **등급 체계**: A(1.0), B(0.6), C(0.2), D(0.0)

### 4. 😌 감정 안정성 (Emotional Stability)
- **측정 요소**: 상담 과정에서 고객 감정 상태 개선 정도
- **계산 공식**: 복합적 감정 변화 분석 (초기→후기 감정 변화)
- **등급 체계**: A~G (7단계, 백분위 기반)

### 5. 🎭 대화 흐름 및 응대 태도 (Stability)
- **측정 요소**: 대화 중단 최소화, 적절한 침묵 유지, 균형잡힌 대화 진행
- **계산 공식**: `interrupt_score*0.3 + silence_score*0.4 + talk_score*0.3`
- **등급 체계**: A~G (7단계, 백분위 기반)

---

## 🤖 OpenAI GPT 피드백 시스템

### 강화된 프롬프트 특징
- **전문가 역할**: 상담사 교육 전문가로 설정
- **지표별 상세 설명**: 각 지표의 의미와 중요성 명시
- **등급 기준 명확화**: 백분위 기준 상세 설명
- **체계적 분석 요청**: 강점/약점을 넘어 구체적 분석 틀 제공
- **실행 중심 코칭**: 즉시 실행 vs 중장기 계획 구분
- **우선순위 기반 접근**: 가장 시급한 개선 영역 선정

### 피드백 출력 형식
```
🌟 핵심 강점
- [상위 지표 기반 강점 분석]
- [고객 만족도 영향 분석]

⚠️ 주요 개선 영역  
- [하위 지표 기반 약점 분석]
- [개선 시 기대효과]

💡 실행 코칭 전략
[즉시 실행]
1. [구체적 행동 방안]
2. [실무 적용 팁]
3. [측정 가능한 목표]

[중장기 개발]
1. [역량 개발 계획]
2. [성과 측정 방법]

🎯 개선 우선순위
1순위: [영역명] - [구체적 근거와 기대효과]
```

---

## 🔧 기술적 핵심 요소

### 1. Min/Max 정규화
- 각 지표별 feature는 **min-max 정규화**(0~1)로 스케일링
- 서로 다른 단위/분포의 feature도 공정하게 가중합 평가 가능
- 신규 데이터 범위 체크 및 자동 갱신

### 2. IQR 기반 이상치 처리
- **Boxplot IQR(Interquartile Range)** 기법으로 이상치 감지
- 극단값은 upper/lower bound로 자동 클리핑
- 평가 체계의 안정성 확보

### 3. 자동 기준선 갱신
- 신규 데이터가 기존 범위 초과 시 자동 재산출
- dummy + 신규 데이터 합쳐서 IQR 클리핑 후 갱신
- 백분위 기반 cut-off 자동 업데이트

### 4. 실제 평가 시스템 연동
- `absolute_grading` 모듈의 실제 계산 결과 사용
- 각 모듈별 `get_*_results()` 함수로 결과 반환
- 정확한 점수/등급을 OpenAI GPT에 전달

---

## 📊 평가 등급 체계

### 백분위 기반 7단계 등급
- **A등급**: 90%ile 이상 (상위 10%)
- **B등급**: 80%ile 이상 (상위 20%)
- **C등급**: 70%ile 이상 (상위 30%)
- **D등급**: 60%ile 이상 (상위 40%)
- **E등급**: 50%ile 이상 (상위 50%)
- **F등급**: 40%ile 이상 (상위 60%)
- **G등급**: 40%ile 미만 (하위 40%)

### 문제해결 4단계 등급
- **A등급**: 1.0 (완전해결)
- **B등급**: 0.6 (대부분해결)
- **C등급**: 0.2 (부분해결)
- **D등급**: 0.0 (해결방안미흡)

---

## 🔄 실행 결과 예시

```
[INFO] new_data.csv로 평가를 진행합니다.
[INFO] absolute_grading 시스템에서 평가 결과를 가져오는 중...
[INFO] 평가 결과 로드 완료 - 총 1개 세션
[세션 99999] 분석 완료!

=== 전체 세션 분석 결과 (총 1개 세션) ===

[세션 ID: 99999]
📊 실제 평가 결과:
  Politeness: 점수 0.553, 등급 D
  Empathy: 점수 0.787, 등급 B
  ProblemSolving: 점수 1.000, 등급 A
  EmotionalStability: 점수 0.398, 등급 G
  Stability: 점수 0.315, 등급 G
----------------------------------------
🤖 OpenAI GPT 피드백:
🌟 핵심 강점
- 문제 해결 역량이 매우 뛰어남 (A등급)
- 공감적 소통 능력이 우수함 (B등급)

⚠️ 주요 개선 영역
- 감정 안정성 개선 시급 (G등급)
- 대화 흐름 및 응대 태도 향상 필요 (G등급)

💡 실행 코칭 전략
[즉시 실행]
1. 깊은 호흡으로 감정 안정성 유지
2. 적절한 침묵과 대화 균형 연습
3. 정중한 언어 사용 체크리스트 활용

[중장기 개발]
1. 감정 관리 전문 교육 수강
2. 대화 기법 워크숍 참여

🎯 개선 우선순위
1순위: 감정 안정성 - 고객 만족도 직결, 즉시 개선 효과 큼
```

---

## 🛠️ 설치 및 실행 환경

### 필요 라이브러리
```bash
pip install pandas numpy openai python-dotenv
```

### 환경 변수 설정
```bash
# .env 파일 생성
OPENAI_API_KEY=your_openai_api_key_here
```

### 실행 환경
- Python 3.7+
- OpenAI API 키 필요
- 평가 데이터 (CSV 형식)

---

## 📈 확장 가능성

- **실시간 평가**: 상담 중 실시간 피드백 제공
- **대시보드**: 웹 기반 시각화 인터페이스
- **API 서비스**: RESTful API로 외부 시스템 연동
- **다국어 지원**: 다양한 언어권 상담사 평가
- **커스텀 지표**: 기업별 특화 평가 지표 추가

---

**🚀 Production-Ready 상담사 평가 자동화 시스템!**

실제 평가 알고리즘 + OpenAI GPT 전문 피드백으로 완성된 실전형 평가 파이프라인입니다. 