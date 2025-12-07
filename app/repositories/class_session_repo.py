# app/repositories/class_session_repo.py
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.class_session import ClassSession


class ClassSessionRepository:
    """Низкоуровневая работа с таблицей class_sessions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, session_id: int) -> ClassSession | None:
        return self.db.get(ClassSession, session_id)

    def list_all(
        self,
        *,
        location_id: Optional[int] = None,
        program_type_id: Optional[int] = None,
        weekday: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> List[ClassSession]:
        stmt = select(ClassSession).order_by(
            ClassSession.weekday,
            ClassSession.start_time,
        )

        if location_id is not None:
            stmt = stmt.where(ClassSession.location_id == location_id)
        if program_type_id is not None:
            stmt = stmt.where(ClassSession.program_type_id == program_type_id)
        if weekday is not None:
            stmt = stmt.where(ClassSession.weekday == weekday)
        if is_active is not None:
            stmt = stmt.where(ClassSession.is_active == is_active)

        return list(self.db.scalars(stmt).all())

    def list_for_location(
        self,
        location_id: int,
        *,
        program_type_id: Optional[int] = None,
        only_active: bool = True,
    ) -> List[ClassSession]:
        stmt = select(ClassSession).where(ClassSession.location_id == location_id)

        if program_type_id is not None:
            stmt = stmt.where(ClassSession.program_type_id == program_type_id)

        if only_active:
            stmt = stmt.where(ClassSession.is_active.is_(True))

        stmt = stmt.order_by(ClassSession.weekday, ClassSession.start_time)
        return list(self.db.scalars(stmt).all())

    def create(self, obj: ClassSession) -> ClassSession:
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, obj: ClassSession) -> None:
        self.db.delete(obj)

