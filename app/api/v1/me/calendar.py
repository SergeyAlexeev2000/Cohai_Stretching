# app/api/v1/me/calendar.py
from datetime import date

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import get_current_user
from app.models.user import User
from app.schemas.calendar import MeCalendarResponse
from app.services.attendance_service import AttendanceService

from . import router


@router.get("/calendar", response_model=MeCalendarResponse)
def my_calendar(
    start_date: date = Query(..., description="Начало диапазона (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Конец диапазона (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MeCalendarResponse:
    """
    Календарь пользователя за указанный период.
    """
    service = AttendanceService(db)
    return service.get_my_calendar(current_user, start_date, end_date)
