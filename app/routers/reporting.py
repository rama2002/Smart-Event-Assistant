from typing import List
from fastapi import APIRouter, HTTPException, Depends
from app.common.auth import get_current_admin_user
from app.database.reporting_db import fetch_event_attendance, fetch_platform_performance
from app.schema.reporting_models import EventAttendance, MonthlySignups
from app.schema.user_models import User

router = APIRouter()

@router.get("/reports/events-attendance/", response_model=List[EventAttendance])
async def get_event_attendance_reports(current_user: User = Depends(get_current_admin_user)):
    data = fetch_event_attendance()
    if not data:
        raise HTTPException(status_code=404, detail="No event attendance data found.")
    return data

@router.get("/reports/platform-performance/", response_model=List[MonthlySignups])
async def get_platform_performance_reports(current_user: User = Depends(get_current_admin_user)):
    data = fetch_platform_performance()
    if not data:
        raise HTTPException(status_code=404, detail="No platform performance data found.")
    return data


