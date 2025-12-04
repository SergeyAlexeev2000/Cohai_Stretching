# app/api/v1/admin_class_sessions.py

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.schemas.class_session import (
    ClassSessionRead,
    ClassSessionCreate,
    ClassSessionUpdate,
)
from app.services.class_session_service import ClassSessionService

router = APIRouter(
    prefix="/admin/class-sessions",
    tags=["admin_class_sessions"],
)


@router.get("", response_model=list[ClassSessionRead])
def list_class_sessions(
    location_id: Optional[int] = Query(
        default=None, description="Фильтр по локации"
    ),
    program_type_id: Optional[int] = Query(
        default=None, description="Фильтр по типу программы"
    ),
    weekday: Optional[int] = Query(
        default=None, description="Фильтр по дню недели (0=Mon..6=Sun)"
    ),
    is_active: Optional[bool] = Query(
        default=None, description="Фильтр по активности"
    ),
    db: Session = Depends(get_db),
):
    service = ClassSessionService(db)
    return service.list_all(
        location_id=location_id,
        program_type_id=program_type_id,
        weekday=weekday,
        is_active=is_active,
    )


@router.get("/{session_id}", response_model=ClassSessionRead)
def get_class_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    service = ClassSessionService(db)
    return service.get_or_404(session_id)


@router.post(
    "",
    response_model=ClassSessionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_class_session(
    payload: ClassSessionCreate,
    db: Session = Depends(get_db),
):
    service = ClassSessionService(db)
    return service.create(payload)


@router.patch(
    "/{session_id}",
    response_model=ClassSessionRead,
)
def update_class_session(
    session_id: int,
    payload: ClassSessionUpdate,
    db: Session = Depends(get_db),
):
    service = ClassSessionService(db)
    return service.update(session_id, payload)


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_class_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    service = ClassSessionService(db)
    service.delete(session_id)
    # тело ответа пустое
