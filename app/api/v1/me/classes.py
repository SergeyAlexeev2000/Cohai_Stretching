# app/api/v1/me/classes.py
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import get_current_user
from app.models.user import User
from app.schemas.attendance import MeClassesResponse
from app.services.attendance_service import AttendanceService

from . import router


@router.get("/classes", response_model=MeClassesResponse)
def my_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MeClassesResponse:
    """
    Мои занятия (записи на занятия), разбитые на upcoming/history.
    """
    service = AttendanceService(db)
    return service.get_my_classes(current_user)
