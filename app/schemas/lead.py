# app/schemas/lead.py
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, EmailStr


# Базовая часть данных лида
class LeadBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None

    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    # Привязки к локации и программе (типы даём такие же,
    # как в ClassSessionBase – int'ы)
    location_id: int
    program_type_id: int

    # Доп. комментарий / заметка администратора
    notes: Optional[str] = None


# То, что приходит с формы "гостевого визита"
class LeadCreateGuestVisit(LeadBase):
    """
    Схема для создания лида гостевого визита.
    Пока не добавляем ничего сверх LeadBase – при необходимости
    можно будет расширить (например, желаемая дата визита и т.п.).
    """
    pass


# То, что отдаём наружу (в ответах API)
class LeadRead(LeadBase):
    id: int

    class Config:
        orm_mode = True  # чтобы Pydantic понимал ORM-объекты SQLAlchemy


__all__ = [
    "LeadBase",
    "LeadCreateGuestVisit",
    "LeadRead",
]
