from __future__ import annotations

from datetime import time
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    # Эти импорты нужны только для type-checker (Pylance / mypy и т.п.)
    # Во время реального запуска Python они не выполняются, поэтому
    # циклического импорта с trainer/location/... не возникает.
    from app.models.location import Location
    from app.models.program_type import ProgramType
    from app.models.membership import MembershipPlan
    from app.models.trainer import Trainer


class ClassSession(Base):
    __tablename__ = "class_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Связи по внешним ключам
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"),
        nullable=False,
    )
    program_type_id: Mapped[int] = mapped_column(
        ForeignKey("program_types.id"),
        nullable=False,
    )
    trainer_id: Mapped[int] = mapped_column(
        ForeignKey("trainers.id"),
        nullable=False,
    )
    membership_plan_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("membership_plans.id"),
        nullable=True,
    )

    # Расписание
    weekday: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 0 = Monday ... 6 = Sunday
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # ORM-связи
    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="class_sessions",
    )
    program_type: Mapped["ProgramType"] = relationship(
        "ProgramType",
        back_populates="class_sessions",
    )
    trainer: Mapped[Optional["Trainer"]] = relationship(
        "Trainer",
        back_populates="class_sessions",
    )
    membership_plan: Mapped[Optional["MembershipPlan"]] = relationship(
        "MembershipPlan",
        back_populates="class_sessions",
    )


__all__ = ["ClassSession"]