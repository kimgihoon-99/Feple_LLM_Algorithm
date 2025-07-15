-- 상담사 평가 결과 저장 테이블 생성
CREATE TABLE counselor_evaluations (
    session_id TEXT PRIMARY KEY,
    
    -- 정중함 평가 결과
    politeness_score DECIMAL(6,3),
    politeness_grade VARCHAR(2),
    
    -- 공감 평가 결과
    empathy_score DECIMAL(6,3),
    empathy_grade VARCHAR(2),
    
    -- 문제해결 평가 결과
    problem_solving_score DECIMAL(6,3),
    problem_solving_grade VARCHAR(2),
    
    -- 감정안정성 평가 결과
    emotional_stability_score DECIMAL(6,3),
    emotional_stability_grade VARCHAR(2),
    
    -- 대화흐름 평가 결과
    stability_score DECIMAL(6,3),
    stability_grade VARCHAR(2),
    
    -- GPT 피드백 전문
    gpt_feedback TEXT,
    
    -- 메타데이터
    evaluation_model VARCHAR(50) DEFAULT 'gpt-4o-mini',
    data_source VARCHAR(100),
    
    -- 타임스탬프
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX idx_counselor_evaluations_created_at ON counselor_evaluations(created_at);

-- Row Level Security (RLS) 비활성화 (팀 내부용)
-- ALTER TABLE counselor_evaluations ENABLE ROW LEVEL SECURITY;

-- 업데이트 시간 자동 갱신 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 업데이트 시간 자동 갱신 트리거
CREATE TRIGGER update_counselor_evaluations_updated_at 
    BEFORE UPDATE ON counselor_evaluations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 테이블 설명 추가
COMMENT ON TABLE counselor_evaluations IS '상담사 5대 지표 LLM 평가 결과 저장 테이블';
COMMENT ON COLUMN counselor_evaluations.session_id IS '상담 세션 ID';
COMMENT ON COLUMN counselor_evaluations.gpt_feedback IS 'OpenAI GPT 생성 피드백 (강점/약점/코칭멘트)';
COMMENT ON COLUMN counselor_evaluations.evaluation_model IS '사용된 LLM 모델명';
COMMENT ON COLUMN counselor_evaluations.data_source IS '평가 데이터 소스 (new_data.csv 또는 dummy_data.csv)'; 