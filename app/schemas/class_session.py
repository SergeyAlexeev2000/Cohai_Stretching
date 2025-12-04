# app/schemas/class_session.py
from __future__ import annotations

from datetime import time, datetime, date
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field


# Базовая схема – общие поля для ClassSession
class ClassSessionBase(BaseModel):
    # ВАЖНО: именно time, как в модели SQLAlchemy
    weekday: int                # 0 = Monday ... 6 = Sunday
    start_time: time            # время начала
    end_time: time              # время окончания

    location_id: int            # FK → Location
    program_type_id: int        # FK → ProgramType
    trainer_id: Optional[int] = None          # FK → Trainer
    membership_plan_id: Optional[int] = None  # FK → MembershipPlan

    capacity: int
    is_active: bool = True

    # Pydantic v2: включаем работу с ORM-моделями
    model_config = ConfigDict(from_attributes=True)


# Для создания (POST и т.п.)
class ClassSessionCreate(ClassSessionBase):
    pass


# Для чтения из БД / ответа API
class ClassSessionRead(ClassSessionBase):
    id: int

    # duration_minutes вычисляем на лету, а не ждём из ORM
    @computed_field
    @property
    def duration_minutes(self) -> int:
        """Длительность занятия в минутах."""
        dt_start = datetime.combine(date.today(), self.start_time)
        dt_end = datetime.combine(date.today(), self.end_time)
        return int((dt_end - dt_start).total_seconds() // 60)


class ClassSessionUpdate(BaseModel):
    """
    Для частичного обновления (PATCH).

    Все поля опциональны: обновляем только то, что пришло.
    """
    weekday: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    location_id: Optional[int] = None
    program_type_id: Optional[int] = None
    trainer_id: Optional[int] = None
    membership_plan_id: Optional[int] = None

    capacity: Optional[int] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "ClassSessionBase",
    "ClassSessionCreate",
    "ClassSessionRead",
    "ClassSessionUpdate",
]
