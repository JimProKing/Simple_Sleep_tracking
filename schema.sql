-- Sleep Tracker 데이터베이스 스키마

-- sleep_records 테이블 생성
CREATE TABLE IF NOT EXISTS sleep_records (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    wake_time TIME,
    sleep_time TIME,
    sleep_duration DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 날짜별 인덱스 생성 (최근 날짜부터 조회하기 위해)
CREATE INDEX IF NOT EXISTS idx_sleep_records_date ON sleep_records(date DESC);

-- updated_at 자동 업데이트를 위한 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- updated_at 자동 업데이트 트리거
DROP TRIGGER IF EXISTS update_sleep_records_updated_at ON sleep_records;
CREATE TRIGGER update_sleep_records_updated_at 
    BEFORE UPDATE ON sleep_records 
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- 테이블 설명 추가
COMMENT ON TABLE sleep_records IS '사용자의 일별 수면 기록을 저장하는 테이블';
COMMENT ON COLUMN sleep_records.id IS '고유 식별자';
COMMENT ON COLUMN sleep_records.date IS '기록 날짜 (YYYY-MM-DD)';
COMMENT ON COLUMN sleep_records.wake_time IS '기상 시간 (HH:MM:SS)';
COMMENT ON COLUMN sleep_records.sleep_time IS '취침 시간 (HH:MM:SS)';
COMMENT ON COLUMN sleep_records.sleep_duration IS '수면 시간 (시간 단위)';
COMMENT ON COLUMN sleep_records.created_at IS '레코드 생성 시각';
COMMENT ON COLUMN sleep_records.updated_at IS '레코드 수정 시각';

-- 샘플 데이터 (선택사항)
-- INSERT INTO sleep_records (date, wake_time, sleep_time, sleep_duration) 
-- VALUES 
--     ('2024-01-29', '07:30:00', '23:00:00', 8.5),
--     ('2024-01-28', '08:00:00', '23:30:00', 8.5),
--     ('2024-01-27', '07:15:00', '22:45:00', 8.5);
