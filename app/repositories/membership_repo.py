# app/repositories/membership_repo.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError  # если используешь общий тип ошибок
from app.models.membership import MembershipPlan


class MembershipRepository:
    """Низкоуровневая работа с тарифами (MembershipPlan)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # --- базовые операции ---

    def list_all(
        self,
        location_id: Optional[int] = None,
        only_active: bool = True,  # зарезервировано на будущее
    ) -> List[MembershipPlan]:
        """
        Универсальный метод:
        - без параметров → вернёт все тарифы,
        - location_id=N → фильтрация по локации.

        Параметр only_active пока не используется, потому что у модели
        MembershipPlan нет поля is_active.
        """
        stmt = select(MembershipPlan)

        if location_id is not None:
            stmt = stmt.where(MembershipPlan.location_id == location_id)

        # if only_active:
        #     stmt = stmt.where(MembershipPlan.is_active.is_(True))

        return list(self.db.scalars(stmt).all())

    def list_for_location(
        self,
        location_id: int,
        only_active: bool = True,
    ) -> List[MembershipPlan]:
        """
        Обёртка для читаемости: все тарифы для одной локации.
        """
        return self.list_all(location_id=location_id, only_active=only_active)

    def get(self, plan_id: int) -> Optional[MembershipPlan]:
        """Получить тариф по id или None, если не найден."""
        return self.db.get(MembershipPlan, plan_id)

    def get_or_404(self, plan_id: int) -> MembershipPlan:
        """Получить тариф по id или кинуть доменную 404-ошибку."""
        plan = self.get(plan_id)
        if plan is None:
            raise AppError(
                code="MEMBERSHIP_PLAN_NOT_FOUND",
                message=f"MembershipPlan with id={plan_id} not found",
                http_status=404,
            )
        return plan


    def get_by_id(self, plan_id: int) -> Optional[MembershipPlan]:
        """
        Совместимость со старым кодом: обёртка над get().
        """
        return self.get(plan_id)

    # --- CRUD-операции ---

    def create(self, plan: MembershipPlan) -> MembershipPlan:
        """
        Создать новый тариф (add + flush).
        ВАЖНО: никаких commit/refresh. Это делает сервис.
        """
        self.db.add(plan)
        self.db.flush()
        return plan

    def save(self, plan: MembershipPlan) -> MembershipPlan:
        """
        Сохранить изменения существующего тарифа (симметрия к create).
        """
        self.db.add(plan)
        self.db.flush()
        return plan

    def delete(self, plan: MembershipPlan) -> None:
        """
        Удалить тариф в рамках текущей транзакции.
        Никаких commit() здесь.
        """
        self.db.delete(plan)

    def delete_by_id(self, plan_id: int) -> None:
        """
        Удалить тариф по id, если существует.
        """
        plan = self.get(plan_id)
        if plan is not None:
            self.db.delete(plan)
