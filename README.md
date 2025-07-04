# 상담사 5대 지표 LLM 평가 시스템

## 프로젝트 개요

이 프로젝트는 상담사 평가를 위해 LLM 기반으로 5대 평가지표(정중함, 공감, 문제해결, 감정안정성, 대화흐름)를 산출하고, 각 지표별 점수와 등급, 그리고 Gemini API를 활용한 피드백(강점/약점/코칭멘트)을 자동 생성하는 실전형 평가 파이프라인입니다.

---

## 디렉토리 구조

```
peple_LLM_v2/
│
├── absolute_grading/         # 각 지표별 절대평가(자동화) 스크립트
│   ├── grade_politeness_auto.py      # 정중함 평가 + evaluate_politeness() 함수
│   ├── grade_empathy_auto.py         # 공감 평가 + evaluate_empathy() 함수
│   ├── grade_emotional_stability_auto.py  # 감정안정성 평가 + evaluate_emotional_stability() 함수
│   ├── grade_stability_auto.py       # 대화흐름 평가 + evaluate_stability() 함수
│   └── grade_problem_solving.py      # 문제해결 평가 + evaluate_problem_solving() 함수
│
├── evaluation_algorithms/    # 각 평가지표별 점수 산출 알고리즘
│   ├── politeness.py
│   ├── empathy.py
│   ├── problem_solving.py
│   ├── emotional_stability.py
│   └── stability.py
│
├── legacy/                   # 구버전(상대평가 등) 평가 스크립트
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
├── LLM_evaluation_batch.py   # 🆕 LLM 기반 통합 평가 및 Gemini 피드백 생성 (메인 스크립트)
└── README.md                 # (바로 이 파일)
```

---

## 주요 기능 및 사용법

### 1. 데이터 준비

- `data/dummy_data.csv` : 기준선 산출용(기존) 데이터
- `data/new_data.csv` : 신규 평가 데이터 (없으면 dummy_data로 평가)
  - **세션 ID 포함**: `session_id` 컬럼이 있으면 LLM 피드백에 표시됨

### 2. cut-off 및 minmax 기준선 산출

```bash
python calculate_cutoff.py
```
- dummy_data.csv를 기반으로 각 지표별 cut-off 및 minmax를 `cutoff/` 폴더에 json으로 저장

### 3. 신규 데이터 평가 (절대평가)

```bash
python batch_grade_all.py
```
- 5개 평가 스크립트(`absolute_grading/grade_*_auto.py`)를 일괄 실행
- `new_data.csv`가 없으면 dummy_data.csv로 평가
- 신규 데이터가 기존 min/max 범위를 벗어나면 cut-off/minmax를 자동 재산출

### 4. 🆕 LLM 기반 통합 평가 및 Gemini 피드백 (메인 기능)

```bash
python LLM_evaluation_batch.py
```

**주요 특징:**
- **자동 모델 선택**: Gemini API에서 사용 가능한 모델을 자동으로 조회하여 최적 모델 선택
- **외부 호출 가능한 평가 함수**: 각 지표별 `evaluate_XXX(df)` 함수로 DataFrame 입력 → 점수/등급 반환
- **세션 ID 포함 피드백**: 세션 ID가 LLM 분석 결과 맨 위에 표시
- **구조화된 프롬프트**: 강점/약점/코칭멘트를 체계적으로 생성

**출력 예시:**
```
## 상담사 평가 분석 (세션 ID: 99999)
- 강점:
  - 정중함 및 언어 품질이 우수함
  - 공감적 소통 능력이 뛰어남
- 약점:
  - 문제 해결 역량 개선 필요
  - 대화 흐름에서 개선 여지 있음
- 개선점/코칭 멘트:
  - 구체적인 해결책 제시 훈련 필요
  - 대화 중단 최소화를 위한 기법 학습 권장
```

---

## 평가 파이프라인의 핵심 요소

### 1. Min/Max 피처 스케일링
- 각 평가지표별 feature(예: 정중함의 honorific_ratio 등)는 **min-max 정규화**(0~1)로 스케일링되어, 서로 다른 단위/분포의 feature도 공정하게 가중합 평가가 가능합니다.
- min/max 값은 충분한 데이터(dummy_data.csv)로 산출하며, 신규 데이터가 들어올 때마다 min/max 범위 내에 있는지 체크합니다.

### 2. Boxplot-IQR 기반 이상치 클리핑
- 신규 데이터 또는 cut-off 재산출 시, **boxplot의 IQR(Interquartile Range) 기법**을 사용해 각 feature별 이상치를 자동으로 감지하고, IQR 범위를 벗어난 값은 해당 upper/lower bound로 "클리핑"합니다.
- 이를 통해 극단적인 이상치가 cut-off 및 min/max 산출에 영향을 주지 않도록 하여, 평가 체계의 안정성을 확보합니다.

### 3. Periodic min/max & cut-off 재산출(자동 갱신)
- 신규 데이터가 기존 min/max 범위를 벗어나면, dummy+신규 데이터를 합쳐 IQR 클리핑 후 **min/max와 cut-off를 함께 재산출**합니다.
- cut-off는 각 지표별 점수 분포의 백분위(90/80/70/...)로 산출되며, 문제해결(problem_solving)은 discrete 점수별 절대 등급 매핑을 사용합니다.
- 이 구조로 인해, 데이터가 추가될 때마다 평가 기준이 자동으로 최신화되고, 이상치에 의한 왜곡도 방지됩니다.

### 4. 🆕 모듈화된 평가 함수
- 각 지표별 평가 알고리즘에 `evaluate_XXX(df)` 함수가 추가되어, 외부에서 DataFrame을 입력받아 점수/등급 DataFrame을 반환
- 이를 통해 LLM 평가 스크립트에서 각 지표별 평가 결과를 쉽게 통합 가능

---

## 평가 방식 요약

- **정중함, 공감, 감정안정성, 대화흐름**:  
  - min-max 정규화 + cut-off(점수 구간) 기반 절대평가
  - cut-off/minmax는 충분한 데이터로 산출, 신규 데이터가 범위 벗어나면 자동 갱신
  - IQR(사분위수) 기반 이상치 클리핑 적용(극단값 영향 최소화)
- **문제해결**:  
  - discrete 점수(0.0, 0.2, 0.6, 1.0)에 대한 절대 등급 매핑

---

## 🆕 LLM 통합 평가 시스템

### 핵심 기능
1. **자동 모델 선택**: Gemini API에서 사용 가능한 모델을 자동 조회하여 최적 모델 선택
2. **세션별 분석**: `new_data.csv`의 각 세션에 대해 5대 지표 평가 후 LLM 피드백 생성
3. **구조화된 출력**: 강점/약점/코칭멘트를 체계적으로 정리하여 제공
4. **세션 ID 추적**: 각 분석 결과에 세션 ID를 명시하여 추적 가능

### 사용법
```bash
# 1. new_data.csv에 평가할 데이터 준비 (session_id 컬럼 포함 권장)
# 2. 환경변수 GEMINI_API_KEY 설정
# 3. 실행
python LLM_evaluation_batch.py
```

---

## 기타 참고

- `legacy/` 폴더는 구버전(상대평가 등) 코드로, 실전 운영에는 사용하지 않음
- `LLM_legacy/` 폴더는 구버전 LLM 평가 스크립트로, 현재는 `LLM_evaluation_batch.py` 사용
- 모든 자동화 스크립트는 robust한 경로 처리, 예외처리, 자동 갱신 구조로 완성
- PowerShell에서 여러 파이썬 파일을 한 번에 실행하려면 `;`(세미콜론) 사용

---

**실전 서비스 수준의 robust한 상담사 평가 자동화 파이프라인!** 
**🆕 LLM 기반 지능형 피드백 시스템으로 업그레이드 완료!** 