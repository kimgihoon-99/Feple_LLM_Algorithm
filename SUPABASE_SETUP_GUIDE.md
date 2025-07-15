# 🗄️ Supabase 연동 설정 가이드

## 1. Supabase 프로젝트 설정

### 1.1 테이블 생성
1. Supabase Dashboard → SQL Editor로 이동
2. `supabase_table_setup.sql` 파일의 내용을 복사하여 실행
3. `counselor_evaluations` 테이블이 생성됨을 확인

### 1.2 API 키 확인
1. Supabase Dashboard → Settings → API로 이동
2. 다음 정보를 복사:
   - **Project URL**: `https://your-project.supabase.co`
   - **anon public key**: `eyJ...` (긴 문자열)

## 2. 환경 변수 설정

### 2.1 .env 파일 수정
프로젝트 루트의 `.env` 파일에서 다음 값들을 실제 값으로 변경:

```env
# 기존 OpenAI 설정 (그대로 유지)
OPENAI_API_KEY=your_actual_openai_api_key

# Supabase 설정 (실제 값으로 변경 필요)
SUPABASE_URL=https://your-actual-project.supabase.co
SUPABASE_KEY=your_actual_supabase_anon_key
```

## 3. 실행 방법

### 3.1 Supabase 연동 버전 실행
```bash
python LLM_evaluation_with_supabase.py
```

### 3.2 실행 결과 확인
- 콘솔에서 Supabase 연결 상태 확인
- 각 세션별 저장 성공/실패 여부 표시
- 최종 저장 통계 출력

## 4. 테이블 구조

### counselor_evaluations 테이블
| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| session_id | TEXT | 상담 세션 ID (기본키) |
| politeness_score | DECIMAL(6,3) | 정중함 점수 |
| politeness_grade | VARCHAR(2) | 정중함 등급 (A~G) |
| empathy_score | DECIMAL(6,3) | 공감 점수 |
| empathy_grade | VARCHAR(2) | 공감 등급 (A~G) |
| problem_solving_score | DECIMAL(6,3) | 문제해결 점수 |
| problem_solving_grade | VARCHAR(2) | 문제해결 등급 (A~D) |
| emotional_stability_score | DECIMAL(6,3) | 감정안정성 점수 |
| emotional_stability_grade | VARCHAR(2) | 감정안정성 등급 (A~G) |
| stability_score | DECIMAL(6,3) | 대화흐름 점수 |
| stability_grade | VARCHAR(2) | 대화흐름 등급 (A~G) |
| gpt_feedback | TEXT | OpenAI GPT 생성 피드백 |
| evaluation_model | VARCHAR(50) | 사용된 LLM 모델명 |
| data_source | VARCHAR(100) | 데이터 소스 |
| created_at | TIMESTAMP | 생성 시간 |
| updated_at | TIMESTAMP | 수정 시간 |

## 5. 데이터 조회 예시

### 5.1 전체 평가 결과 조회
```sql
SELECT * FROM counselor_evaluations 
ORDER BY created_at DESC;
```

### 5.2 특정 세션 조회
```sql
SELECT * FROM counselor_evaluations 
WHERE session_id = 'session_001';
```

### 5.3 등급별 통계
```sql
SELECT 
    politeness_grade,
    COUNT(*) as count
FROM counselor_evaluations 
GROUP BY politeness_grade 
ORDER BY politeness_grade;
```

### 5.4 평균 점수 조회
```sql
SELECT 
    AVG(politeness_score) as avg_politeness,
    AVG(empathy_score) as avg_empathy,
    AVG(problem_solving_score) as avg_problem_solving,
    AVG(emotional_stability_score) as avg_emotional_stability,
    AVG(stability_score) as avg_stability
FROM counselor_evaluations;
```

## 6. 문제 해결

### 6.1 연결 실패 시
```
[ERROR] Supabase 연결 실패: ...
```
- `.env` 파일의 SUPABASE_URL과 SUPABASE_KEY 확인
- Supabase 프로젝트가 활성화되어 있는지 확인
- 네트워크 연결 상태 확인

### 6.2 테이블 생성 실패 시
- SQL Editor에서 권한 확인
- 테이블명 중복 여부 확인
- SQL 구문 오류 확인

### 6.3 데이터 저장 실패 시
```
[SUPABASE ERROR] 세션 session_001 저장 중 오류: ...
```
- 테이블 스키마와 데이터 타입 일치 여부 확인
- Row Level Security (RLS) 정책 확인
- API 키 권한 확인

## 7. 보안 고려사항

### 7.1 API 키 관리
- `.env` 파일을 `.gitignore`에 추가
- 프로덕션에서는 service role key 사용 고려
- 정기적인 API 키 순환

### 7.2 Row Level Security
- 필요시 RLS 정책 설정
- 사용자별 데이터 접근 제어
- 감사 로그 활성화

## 8. 모니터링 및 백업

### 8.1 데이터 모니터링
- Supabase Dashboard에서 실시간 모니터링
- 데이터 증가 추이 확인
- 오류 로그 정기 확인

### 8.2 백업 전략
- 정기적인 데이터 백업 설정
- 중요 데이터 별도 저장
- 복구 절차 문서화

---

**🎯 완료 체크리스트:**
- [ ] Supabase 프로젝트 생성
- [ ] `counselor_evaluations` 테이블 생성
- [ ] API 키 확인 및 `.env` 파일 설정
- [ ] 연동 테스트 실행
- [ ] 데이터 저장 및 조회 확인
- [ ] 팀원들과 접근 권한 설정 