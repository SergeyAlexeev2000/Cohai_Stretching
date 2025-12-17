# app/api/v1/admin/admin_class_sessions.py

from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import require_role
from app.models.user import UserRole

from app.schemas.class_session import (
    ClassSessionRead,
    ClassSessionCreate,
    ClassSessionUpdate,
)
from app.services.class_session_service import ClassSessionService


# ---------------------------------------------------------------------------
#   ROUTER — доступ ADMIN и SUPERADMIN
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/admin/class-sessions",
    tags=["admin_class_sessions"],
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.SUPERADMIN))],
)


# ---------------------------------------------------------------------------
#   GET /admin/class-sessions — список с фильтрами
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ClassSessionRead])
def list_class_sessions(
    location_id: Optional[int] = Query(default=None),
    trainer_id: Optional[int] = Query(default=None),
    program_type_id: Optional[int] = Query(default=None),
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    """
    Список занятий с фильтрами (админская версия).
    """
    service = ClassSessionService(db)
    return service.list_sessions_admin(
        location_id=location_id,
        trainer_id=trainer_id,
        program_type_id=program_type_id,
        include_inactive=include_inactive,
    )


# ---------------------------------------------------------------------------
#   GET /admin/class-sessions/{session_id}
# ---------------------------------------------------------------------------

@router.get("/{session_id}", response_model=ClassSessionRead)
def get_class_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    service = ClassSessionService(db)
    return service.get_session(session_id)


# ---------------------------------------------------------------------------
#   POST /admin/class-sessions — создать сессию
# ---------------------------------------------------------------------------

@router.post("", response_model=ClassSessionRead, status_code=status.HTTP_201_CREATED)
def create_class_session(
    payload: ClassSessionCreate,
    db: Session = Depends(get_db),
):
    service = ClassSessionService(db)
    return service.create_session(payload)


# ---------------------------------------------------------------------------
#   PATCH /admin/class-sessions/{session_id} — обновить занятие
# ---------------------------------------------------------------------------

@router.patch("/{session_id}", response_model=ClassSessionRead)
def update_class_session(
    session_id: int,
    payload: ClassSessionUpdate,
    db: Session = Depends(get_db),
):
    service = ClassSessionService(db)
    return service.update_session(session_id, payload)

# ---------------------------------------------------------------------------
#   POST /admin/class-sessions/{session_id}/cancel — отменить занятие
# ---------------------------------------------------------------------------

@router.post(
    "/{session_id}/cancel",
    response_model=ClassSessionRead,
    status_code=status.HTTP_200_OK,
)
def cancel_class_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    """
    Отменить занятие — пометить is_active = False (идемпотентно).
    Видно только ADMIN и SUPERADMIN (задаётся в dependencies у router).
    """
    service = ClassSessionService(db)
    return service.cancel_session(session_id)

# ---------------------------------------------------------------------------
#   DELETE /admin/class-sessions/{session_id}
# ---------------------------------------------------------------------------

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    service = ClassSessionService(db)
    service.delete_session(session_id)
    return None
