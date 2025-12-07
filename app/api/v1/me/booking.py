# app/api/v1/me/booking.py
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import get_current_user
from app.models.user import User
from app.schemas.attendance import ClassBookingRequest, ClassCancelRequest, MeClassItem
from app.services.attendance_service import AttendanceService

from . import router


@router.post("/classes/book", response_model=MeClassItem)
def book_class(
    payload: ClassBookingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MeClassItem:
    """
    Записаться на занятие (конкретная дата).
    """
    service = AttendanceService(db)
    return service.book_class(current_user, payload)


@router.post("/classes/cancel", response_model=MeClassItem)
def cancel_class(
    payload: ClassCancelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MeClassItem:
    """
    Отмена своей записи на занятие.
    """
    service = AttendanceService(db)
    return service.cancel_class(current_user, payload)
