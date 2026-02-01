from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from typing import Optional
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient  # ← 변경된 import

load_dotenv(override=True)

app = FastAPI(title="Sleep Tracker API")

# CORS 설정 (프론트엔드에서 호출 가능하게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase/PostgREST 클라이언트 초기화
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"DEBUG - SUPABASE_URL: {SUPABASE_URL}")
print(f"DEBUG - SUPABASE_KEY: {SUPABASE_KEY[:20] if SUPABASE_KEY else 'NOT SET'}...")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL 또는 SUPABASE_KEY가 .env에 없습니다.")

# PostgREST 클라이언트 생성 (supabase-py의 내부 동작과 동일)
supabase: SyncPostgrestClient = SyncPostgrestClient(
    base_url=f"{SUPABASE_URL}/rest/v1",
    headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
)

# 인증 코드
WAKE_CODE = "666"
SLEEP_CODE = "999"

# Pydantic 모델
class TimeRecord(BaseModel):
    auth_code: str
    record_type: str  # "wake" or "sleep"

class SleepRecord(BaseModel):
    id: Optional[int] = None
    date: str
    wake_time: Optional[str] = None
    sleep_time: Optional[str] = None
    sleep_duration: Optional[float] = None

# 한국 시간대 상수
KST = ZoneInfo("Asia/Seoul")

@app.get("/")
async def root():
    """루트 경로에서 index.html 반환"""
    return FileResponse("index.html")

# 정적 파일 마운트 (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="."), name="static")

@app.post("/record")
async def record_time(record: TimeRecord):
    """기상 또는 취침 시간 기록"""
    if record.record_type == "wake" and record.auth_code != WAKE_CODE:
        raise HTTPException(401, "잘못된 기상 인증코드입니다")
    if record.record_type == "sleep" and record.auth_code != SLEEP_CODE:
        raise HTTPException(401, "잘못된 취침 인증코드입니다")
    if record.record_type not in ["wake", "sleep"]:
        raise HTTPException(400, "record_type은 'wake' 또는 'sleep'이어야 합니다")

    now = datetime.now(KST)
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    try:
        # 오늘 기록 확인
        res = supabase.table("sleep_records") \
            .select("*") \
            .eq("date", current_date) \
            .execute()

        data = {}
        if record.record_type == "wake":
            data["wake_time"] = current_time
        else:
            data["sleep_time"] = current_time

        if res.data:  # 기존 기록 있음 → 업데이트
            existing = res.data[0]
            if record.record_type == "wake" and existing.get("sleep_time"):
                duration = calculate_sleep_duration(
                    existing["sleep_time"], current_time
                )
                data["sleep_duration"] = duration

            supabase.table("sleep_records") \
                .update(data) \
                .eq("date", current_date) \
                .execute()
        else:  # 새 기록
            insert_data = {
                "date": current_date,
                **({"wake_time": current_time} if record.record_type == "wake" else {"sleep_time": current_time})
            }
            supabase.table("sleep_records").insert(insert_data).execute()

        return {
            "success": True,
            "message": f"{'기상' if record.record_type == 'wake' else '취침'} 시간이 기록되었습니다",
            "date": current_date,
            "time": current_time
        }

    except Exception as e:
        raise HTTPException(500, f"Supabase 오류: {str(e)}")

@app.get("/records")
async def get_records(limit: int = 30):
    """최근 N일 기록 조회"""
    try:
        res = supabase.table("sleep_records") \
            .select("*") \
            .order("date", desc=True) \
            .limit(limit) \
            .execute()

        return {
            "success": True,
            "records": res.data
        }
    except Exception as e:
        raise HTTPException(500, f"조회 오류: {str(e)}")

@app.get("/records/{date}")
async def get_record_by_date(date: str):
    """특정 날짜 기록 조회"""
    try:
        res = supabase.table("sleep_records") \
            .select("*") \
            .eq("date", date) \
            .execute()

        if res.data:
            return {
                "success": True,
                "record": res.data[0]
            }
        else:
            return {
                "success": True,
                "record": None,
                "message": "해당 날짜의 기록이 없습니다"
            }
    except Exception as e:
        raise HTTPException(500, f"조회 오류: {str(e)}")

def calculate_sleep_duration(sleep_time: str, wake_time: str) -> float:
    """수면 시간 계산 (시간 단위)"""
    try:
        sleep_dt = datetime.strptime(sleep_time, "%H:%M:%S")
        wake_dt = datetime.strptime(wake_time, "%H:%M:%S")

        if sleep_dt > wake_dt:
            wake_dt = wake_dt.replace(day=wake_dt.day + 1)

        duration = (wake_dt - sleep_dt).total_seconds() / 3600
        return round(duration, 2)
    except:
        return 0.0

app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)