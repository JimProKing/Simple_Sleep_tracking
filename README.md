# 수면 시간 관리 앱

FastAPI와 Supabase를 사용한 기상/취침 시간 관리 애플리케이션입니다.

## 기능

- 🌅 기상 시간 기록 (인증코드: 666)
- 🌙 취침 시간 기록 (인증코드: 999)
- 📊 수면 기록 모니터링
- ⏱️ 자동 수면 시간 계산
- 📈 평균 수면 시간 통계

## 설치 방법

### 1. Supabase 테이블 생성

Supabase 프로젝트의 SQL Editor에서 다음 쿼리를 실행하세요:

```sql
CREATE TABLE sleep_records (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    wake_time TIME,
    sleep_time TIME,
    sleep_duration DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 날짜별 인덱스 생성
CREATE INDEX idx_sleep_records_date ON sleep_records(date DESC);

-- updated_at 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sleep_records_updated_at BEFORE UPDATE
    ON sleep_records FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();
```

### 2. Python 패키지 설치

```bash
pip3 install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 Supabase 정보를 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 내용:
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

Supabase 프로젝트 설정에서:
- Project URL: Settings → API → Project URL
- anon/public key: Settings → API → Project API keys → anon public

### 4. 서버 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

### 5. 웹 인터페이스 사용

`index.html` 파일을 브라우저에서 열거나, 간단한 HTTP 서버를 실행하세요:

```bash
# Python 3
python -m http.server 8080
```

그 다음 `http://localhost:8080/index.html`로 접속하세요.

## API 엔드포인트

### POST /record
기상 또는 취침 시간 기록

**요청 본문:**
```json
{
    "auth_code": "666",
    "record_type": "wake"
}
```

**응답:**
```json
{
    "success": true,
    "message": "기상 시간이 기록되었습니다",
    "time": "07:30:00",
    "date": "2024-01-29"
}
```

### GET /records
최근 수면 기록 조회

**쿼리 파라미터:**
- `limit`: 조회할 레코드 수 (기본값: 30)

**응답:**
```json
{
    "success": true,
    "records": [
        {
            "id": 1,
            "date": "2024-01-29",
            "wake_time": "07:30:00",
            "sleep_time": "23:00:00",
            "sleep_duration": 8.5
        }
    ]
}
```

### GET /records/{date}
특정 날짜의 기록 조회

**응답:**
```json
{
    "success": true,
    "record": {
        "id": 1,
        "date": "2024-01-29",
        "wake_time": "07:30:00",
        "sleep_time": "23:00:00",
        "sleep_duration": 8.5
    }
}
```

## 인증 코드

- 기상: `666`
- 취침: `999`

## 주의사항

- 수면 시간은 취침 시간과 다음 날 기상 시간을 기반으로 계산됩니다
- 같은 날짜에 여러 번 기록하면 마지막 기록으로 업데이트됩니다
- 모니터링은 인증 없이 가능하며, 기록 입력 시에만 인증이 필요합니다

## 기술 스택

- **Backend**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript
- **Python Version**: 3.8+
