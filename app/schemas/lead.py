# app/schemas/lead.py
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

from app.models.lead import LeadStatus

# Базовая часть данных лида
class LeadBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    # Вариант 2: цельное имя (для тестов и упрощённых форм)
    full_name: Optional[str] = None

    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    location_id: int
    program_type_id: Optional[int] = None

    notes: Optional[str] = None
    message: str | None = None

    @field_validator("full_name", mode="before")
    @classmethod
    def ensure_full_name(cls, v, values):
        """
        Если full_name не передан, но есть first_name / last_name,
        собираем full_name автоматически.

        Если ничего нет — кидаем ошибку валидации.
        """
        if v:
            return v

        first = values.get("first_name")
        last = values.get("last_name")

        if first or last:
            return f"{first or ''} {last or ''}".strip()

        raise ValueError(
            "Either full_name or first_name/last_name must be provided"
        )

# То, что приходит с формы "гостевого визита"
class LeadCreateGuestVisit(LeadBase):
    """
    Схема для создания лида гостевого визита.
    Пока не добавляем ничего сверх LeadBase – при необходимости
    можно будет расширить (например, желаемая дата визита и т.п.).
    """
    location_id: int | None = None


# То, что отдаём наружу (в ответах API)
class LeadRead(LeadBase):
    id: int
    created_at: datetime
    is_processed: bool

    status: LeadStatus
    assigned_trainer_id: int | None = None
    assigned_admin_id: int | None = None

    class Config:
        orm_mode = True  # чтобы Pydantic понимал ORM-объекты SQLAlchemy


#И схема для обновления админом/тренером:
class LeadUpdateAdmin(BaseModel):
    status: LeadStatus | None = None
    assigned_trainer_id: int | None = None
    assigned_admin_id: int | None = None


__all__ = [
    "LeadBase",
    "LeadCreateGuestVisit",
    "LeadRead",
]
