# app/schemas/program_type.py

from typing import Optional
from pydantic import BaseModel


class ProgramTypeBase(BaseModel):
    """Базовые данные о типе программы (йога, стретчинг и т.п.)."""
    name: str
    description: Optional[str] = None
    is_group: bool  # ← добавили это поле

    class Config:
        orm_mode = True


class ProgramTypeRead(ProgramTypeBase):
    """То, что отдаём наружу в API."""
    id: int


class ProgramTypeCreate(ProgramTypeBase):
    """Если когда-нибудь будем создавать типы программ через API."""
    pass


class ProgramTypeUpdate(BaseModel):
    """Обновление типа программы (все поля необязательны)."""
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


__all__ = [
    "ProgramTypeBase",
    "ProgramTypeRead",
    "ProgramTypeCreate",
    "ProgramTypeUpdate",
]
