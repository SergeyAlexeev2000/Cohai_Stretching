# app/repositories/lead_repo.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lead import Lead, LeadStatus


class LeadRepository:
    """Низкоуровневая работа с таблицей leads."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # --- базовые операции ---

    def get(self, lead_id: int) -> Optional[Lead]:
        """Вернуть лида по id или None, если не найден."""
        return self.db.get(Lead, lead_id)

    def list_all(self) -> List[Lead]:
        """Все лиды, от новых к старым."""
        stmt = select(Lead).order_by(Lead.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def list_by_user(self, user_id: int) -> List[Lead]:
        """Лиды, созданные конкретным пользователем."""
        stmt = (
            select(Lead)
            .where(Lead.user_id == user_id)
            .order_by(Lead.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_by_trainer(self, trainer_id: int) -> List[Lead]:
        """Лиды, закреплённые за конкретным тренером (для тренерских экранов)."""
        stmt = (
            select(Lead)
            .where(Lead.trainer_id == trainer_id)
            .order_by(Lead.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_for_admin(
        self,
        *,
        status: Optional[LeadStatus] = None,
        trainer_id: Optional[int] = None,
    ) -> List[Lead]:
        """
        Фильтрация для админских списков.

        Важно: здесь НЕТ логики ролей, только фильтры по полям.
        Решение, кто имеет право видеть этот список, принимает сервис.
        """
        stmt = select(Lead).order_by(Lead.created_at.desc())

        if status is not None:
            # в БД статус хранится как строка
            stmt = stmt.where(Lead.status == status.value)

        if trainer_id is not None:
            stmt = stmt.where(Lead.trainer_id == trainer_id)

        return list(self.db.scalars(stmt).all())

    def create(self, lead: Lead) -> Lead:
        """
        Создаём объект, но здесь только add+flush.
        Коммит делается на уровне сервиса.
        """
        self.db.add(lead)
        self.db.flush()  # чтобы появился id, не коммитя транзакцию
        return lead

    def delete(self, lead: Lead) -> None:
        """Пометить лида на удаление в текущей транзакции."""
        self.db.delete(lead)
        # НИКАКОГО commit здесь
