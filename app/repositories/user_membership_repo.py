# app/repositories/user_membership_repo.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.membership import Membership


class UserMembershipRepository:
    """
    Низкоуровневая работа с конкретными абонементами пользователя (Membership).
    Не путать с MembershipPlan.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # --- базовые операции ---

    def get(self, membership_id: int) -> Optional[Membership]:
        """Вернуть абонемент по id или None."""
        return self.db.get(Membership, membership_id)

    def get_or_404(self, membership_id: int) -> Membership:
        """Вернуть абонемент по id или кинуть 404."""
        obj = self.get(membership_id)
        if obj is None:
            raise AppError(
                code="MEMBERSHIP_NOT_FOUND",
                message=f"Membership with id={membership_id} not found",
                http_status=404,
            )
        return obj


    def list_for_user(self, user_id: int) -> List[Membership]:
        """
        Все абонементы конкретного пользователя.
        Сортировку можно легко менять (по дате начала, по окончанию и т.п.).
        """
        stmt = (
            select(Membership)
            .where(Membership.user_id == user_id)
            .order_by(Membership.end_date.desc())
        )
        return list(self.db.scalars(stmt).all())

    # --- CRUD на будущее (если понадобится создавать/менять Membership через сервисы) ---

    def create(self, membership: Membership) -> Membership:
        """Создать новый абонемент (add + flush). Коммит — в сервисе."""
        self.db.add(membership)
        self.db.flush()
        return membership

    def save(self, membership: Membership) -> Membership:
        """Сохранить изменения существующего абонемента."""
        self.db.add(membership)
        self.db.flush()
        return membership

    def delete(self, membership: Membership) -> None:
        """Удалить абонемент в рамках текущей транзакции."""
        self.db.delete(membership)
