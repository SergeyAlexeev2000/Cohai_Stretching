# app/schemas/membership.py

from typing import Optional

from pydantic import BaseModel


class MembershipPlanBase(BaseModel):
    """Базовые данные о тарифе/абонементе."""
    name: str

    class Config:
        orm_mode = True


class MembershipPlanRead(MembershipPlanBase):
    """То, что отдаём наружу в API."""
    id: int


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