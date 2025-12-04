# app/services/schedule_service.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.class_session import ClassSession


class ScheduleService:
    """Публичное расписание занятий."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_schedule_for_location(
        self,
        location_id: int,
        program_type_id: Optional[int] = None,
    ) -> List[ClassSession]:
        """
        Вернуть занятия для заданной локации.

        Если передан program_type_id — дополнительно фильтруем по типу программы.
        В дальнейшем можно добавить:
        - фильтрацию по дням недели
        - только активные слоты и т.п.
        """
        stmt = (
            select(ClassSession)
            .where(ClassSession.location_id == location_id)
        )

        if program_type_id is not None:
            stmt = stmt.where(ClassSession.program_type_id == program_type_id)

        stmt = stmt.order_by(ClassSession.weekday, ClassSession.start_time)

        return list(self.db.scalars(stmt).all())
