# app/api/v1/public/schedule.py
from typing import Optional

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.schemas.class_session import ClassSessionRead
from app.services.schedule_service import ScheduleService

from . import router


@router.get("/schedule", response_model=list[ClassSessionRead])
def get_schedule(
    location_id: int = Query(...),
    program_type_id: Optional[int] = Query(
        default=None,
        description="Фильтрация по типу программы. Если не задано — вернуть все занятия локации.",
    ),
    db: Session = Depends(get_db),
):
    service = ScheduleService(db)
    return service.get_schedule_for_location(
        location_id=location_id,
        program_type_id=program_type_id,
    )
