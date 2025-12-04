# app/schemas/membership.py
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class MembershipPlanBase(BaseModel):
    """Базовые данные о тарифе/абонементе."""
    name: str
    description: Optional[str] = None
    price: float
    location_id: int      # FK -> locations.id
    # duration_days: int
    # is_active: bool = True
    # аналог orm_mode=True в pydantic v2
    model_config = ConfigDict(from_attributes=True)


class MembershipPlanRead(MembershipPlanBase):
    """То, что отдаём наружу в API."""
    id: int
    
    class Config:
        orm_mode = True


class MembershipPlanCreate(MembershipPlanBase):
    """Если когда-нибудь понадобится создавать тарифы через API."""
    pass


class MembershipPlanUpdate(BaseModel):
    """Схема для обновления тарифа (необязательные поля)."""
    name: Optional[str] = None

    class Config:
        orm_mode = True

class MembershipRead(BaseModel):
    """
    Конкретный абонемент пользователя (Membership) для отдачи в API.
    """

    id: int
    membership_plan_id: int

    start_date: date
    end_date: date

    visits_total: int | None = None
    visits_used: int

    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MembershipListResponse(BaseModel):
    """
    Ответ для /api/v1/me/memberships:
    - active: активные абонементы
    - history: истёкшие / отменённые / замороженные
    """

    active: list[MembershipRead]
    history: list[MembershipRead]


__all__ = [
    "MembershipPlanBase",
    "MembershipPlanRead",
    "MembershipPlanCreate",
    "MembershipPlanUpdate",
]