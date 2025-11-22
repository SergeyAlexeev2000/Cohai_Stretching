# app/schemas/membership.py
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict

class MembershipPlanBase(BaseModel):
    """Базовые данные о тарифе/абонементе."""
    name: str
    description: Optional[str] = None
    price: float
    duration_days: int          # можно и int, но float чуть гибче
    location_id: int      # FK -> locations.id
    is_active: bool = True
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


__all__ = [
    "MembershipPlanBase",
    "MembershipPlanRead",
    "MembershipPlanCreate",
    "MembershipPlanUpdate",
]