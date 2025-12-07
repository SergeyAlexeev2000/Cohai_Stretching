# app/services/schedule_service.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.class_session import ClassSession
from app.repositories.class_session_repo import ClassSessionRepository


class ScheduleService:
    """Публичное расписание занятий."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ClassSessionRepository(db)

    def get_schedule_for_location(
        self,
        location_id: int,
        program_type_id: Optional[int] = None,
    ) -> List[ClassSession]:
        """
        Вернуть занятия для заданной локации.

        Если передан program_type_id — дополнительно фильтруем по типу программы.
        """
        return self.repo.list_for_location(
            location_id=location_id,
            program_type_id=program_type_id,
            only_active=True,
        )
