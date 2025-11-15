# app/schemas/class_session.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Базовая схема – то, что нужно, чтобы описать занятие
class ClassSessionBase(BaseModel):
    start_time: datetime          # когда начинается
    duration_minutes: int         # длительность в минутах

    location_id: int              # FK → Location
    program_type_id: int          # FK → ProgramType
    trainer_id: Optional[int] = None  # FK → Trainer (может быть пустым)


# Для создания (POST-запросы и т.п.)
class ClassSessionCreate(ClassSessionBase):
    pass


# Для чтения из БД / ответа API
class ClassSessionRead(ClassSessionBase):
    id: int

    class Config:
        orm_mode = True  # чтобы работать с ORM-моделями SQLAlchemy


__all__ = [
    "ClassSessionBase",
    "ClassSessionCreate",
    "ClassSessionRead",
]