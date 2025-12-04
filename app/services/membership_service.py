# app/services/membership_service.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import MembershipPlan

from app.schemas.membership import (
    MembershipPlanCreate,
    MembershipPlanUpdate,
)
from app.core.exceptions import AppError


class MembershipService:
    """Бизнес-логика для абонементов (membership_plans)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(
        self,
        location_id: Optional[int] = None,
        only_active: bool = True,  # пока просто игнорируем, но параметр оставляем
    ) -> List[MembershipPlan]:
        """
        Вернуть список абонементов.

        - если location_id задан — фильтруем по локации;
        - only_active пока не используется (в схеме нет поля is_active),
          но параметр оставляем для будущего расширения.
        """
        stmt = select(MembershipPlan)

        if location_id is not None:
            stmt = stmt.where(MembershipPlan.location_id == location_id)

        stmt = stmt.order_by(MembershipPlan.id)
        return list(self.db.scalars(stmt).all())

    def get(self, membership_id: int) -> Optional[MembershipPlan]:
        """Вернуть один абонемент по id или None."""
        stmt = select(MembershipPlan).where(MembershipPlan.id == membership_id)
        return self.db.scalars(stmt).first()
    
    # --- Вспомогательное: для админки ---

    def get_or_404(self, membership_id: int) -> MembershipPlan:
        """
        Вернуть абонемент или кинуть AppError(404).

        Используется админскими эндпоинтами.
        """
        membership = self.get(membership_id)
        if membership is None:
            raise AppError(
                code="MEMBERSHIP_NOT_FOUND",
                message=f"MembershipPlan with id={membership_id} not found",
                http_status=404,
                extra={"membership_id": membership_id},
            )
        return membership

    # --- CRUD для админки ---

    def create(self, payload: MembershipPlanCreate) -> MembershipPlan:
        """Создать новый тариф/абонемент."""
        membership = MembershipPlan(
            name=payload.name,
            description=payload.description,
            price=payload.price,
            location_id=payload.location_id,
        )
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def update(
        self,
        membership_id: int,
        payload: MembershipPlanUpdate,
    ) -> MembershipPlan:
        """
        Обновить существующий тариф (частично).

        Все поля в MembershipPlanUpdate — OPTIONAL, поэтому обновляем только
        те, что реально переданы (exclude_unset=True).
        """
        membership = self.get_or_404(membership_id)

        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(membership, field, value)

        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def delete(self, membership_id: int) -> None:
        """Удалить тариф (жёстко)."""
        membership = self.get_or_404(membership_id)
        self.db.delete(membership)
        self.db.commit()
