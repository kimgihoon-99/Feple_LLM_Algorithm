-- RLS 비활성화 (가장 간단한 해결책)
ALTER TABLE counselor_evaluations DISABLE ROW LEVEL SECURITY;

-- 또는 모든 사용자에게 삽입 권한을 허용하는 정책 생성
-- CREATE POLICY "Enable insert for all users" ON counselor_evaluations
-- FOR INSERT WITH CHECK (true);

-- 모든 사용자에게 조회 권한을 허용하는 정책 생성
-- CREATE POLICY "Enable read for all users" ON counselor_evaluations
-- FOR SELECT USING (true); 