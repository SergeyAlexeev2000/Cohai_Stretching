# app/repositories/class_session_repo.py
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError  # если уже есть общий AppError
from app.models.class_session import ClassSession


class ClassSessionRepository:
    """Низкоуровневая работа с таблицей class_sessions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # --- базовые операции ---

    def get(self, session_id: int) -> ClassSession | None:
        """Вернуть занятие по id или None, если не найдено."""
        return self.db.get(ClassSession, session_id)

    def get_or_404(self, session_id: int) -> ClassSession:
        """Вернуть занятие по id или кинуть 404-ошибку уровня домена."""
        obj = self.get(session_id)
        if obj is None:
            raise AppError(
                code="CLASS_SESSION_NOT_FOUND",
                message=f"ClassSession with id={session_id} not found",
                http_status=404,
            )
        return obj

    def list_all(
        self,
        *,
        location_id: Optional[int] = None,
        program_type_id: Optional[int] = None,
        weekday: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> List[ClassSession]:
        """
        Все занятия с опциональными фильтрами, для админских списков / сервисов.

        ВАЖНО: здесь только фильтры по полям, никаких решений по правам доступа.
        """
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
        """
        Занятия для конкретной локации (используется в публичном расписании и т.п.).
        """
        stmt = select(ClassSession).where(ClassSession.location_id == location_id)

        if program_type_id is not None:
            stmt = stmt.where(ClassSession.program_type_id == program_type_id)

        if only_active:
            stmt = stmt.where(ClassSession.is_active.is_(True))

        stmt = stmt.order_by(ClassSession.weekday, ClassSession.start_time)
        return list(self.db.scalars(stmt).all())

    def create(self, obj: ClassSession) -> ClassSession:
        """
        Создаём новое занятие (add + flush).
        Коммит делается на уровне сервиса.
        """
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, obj: ClassSession) -> None:
        """
        Пометить занятие на удаление в текущей транзакции.
        Здесь НЕТ commit().
        """
        self.db.delete(obj)

    # опционально — если захочется централизованный update

    def save(self, obj: ClassSession) -> ClassSession:
        """
        Явное сохранение уже существующего объекта (если нужно симметричное API).
        По сути просто ensure, что объект в сессии.
        """
        self.db.add(obj)
        self.db.flush()
        return obj
