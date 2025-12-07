# app/services/class_session_service.py

from __future__ import annotations

from datetime import datetime, date, time
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.class_session import ClassSession
from app.schemas.class_session import (
    ClassSessionCreate,
    ClassSessionUpdate,
)
from app.core.exceptions import AppError
from app.repositories.class_session_repo import ClassSessionRepository


def _validate_time_range(start: time, end: time) -> None:
    """Проверка, что время окончания позже начала."""
    dt_start = datetime.combine(date.today(), start)
    dt_end = datetime.combine(date.today(), end)
    if dt_end <= dt_start:
        raise AppError(
            code="INVALID_TIME_RANGE",
            message="end_time must be later than start_time",
            http_status=400,
        )


class ClassSessionService:
    """Бизнес-логика для расписания (class_sessions) в админке."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ClassSessionRepository(db)

    # --- базовые операции ---

    def list_all(
        self,
        *,
        location_id: Optional[int] = None,
        program_type_id: Optional[int] = None,
        weekday: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> List[ClassSession]:
        """
        Список занятий с фильтрами.

        Фильтры все опциональные.
        """
        return self.repo.list_all(
            location_id=location_id,
            program_type_id=program_type_id,
            weekday=weekday,
            is_active=is_active,
        )

    def get_or_404(self, session_id: int) -> ClassSession:
        """Вернуть занятие или 404."""
        obj = self.repo.get(session_id)
        if obj is None:
            raise AppError(
                code="CLASS_SESSION_NOT_FOUND",
                message=f"ClassSession with id={session_id} not found",
                http_status=404,
                extra={"class_session_id": session_id},
            )
        return obj

    # --- CRUD ---

    def create(self, payload: ClassSessionCreate) -> ClassSession:
        """Создать занятие."""
        _validate_time_range(payload.start_time, payload.end_time)
        if payload.capacity <= 0:
            raise AppError(
                code="INVALID_CAPACITY",
                message="capacity must be positive",
                http_status=400,
            )

        obj = ClassSession(
            weekday=payload.weekday,
            start_time=payload.start_time,
            end_time=payload.end_time,
            location_id=payload.location_id,
            program_type_id=payload.program_type_id,
            trainer_id=payload.trainer_id,
            membership_plan_id=payload.membership_plan_id,
            capacity=payload.capacity,
            is_active=payload.is_active,
        )
        self.repo.create(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, session_id: int, payload: ClassSessionUpdate) -> ClassSession:
        """Частично обновить занятие."""
        obj = self.get_or_404(session_id)

        data = payload.model_dump(exclude_unset=True)

        # сначала проверим время, если оно меняется
        new_start = data.get("start_time", obj.start_time)
        new_end = data.get("end_time", obj.end_time)
        if ("start_time" in data) or ("end_time" in data):
            _validate_time_range(new_start, new_end)

        # capacity (если явно прислали)
        if "capacity" in data and data["capacity"] is not None:
            if data["capacity"] <= 0:
                raise AppError(
                    code="INVALID_CAPACITY",
                    message="capacity must be positive",
                    http_status=400,
                )

        for field, value in data.items():
            setattr(obj, field, value)

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, session_id: int) -> None:
        """Удалить занятие."""
        obj = self.get_or_404(session_id)
        self.repo.delete(obj)
        self.db.commit()
