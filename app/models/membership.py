# app/models/membership.py
from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.class_session import ClassSession


class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    # длительность абонемента в днях
    duration_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )

    # активен ли тариф
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # связь с локацией
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"),
        nullable=False,
    )
    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="membership_plans",
    )

    # связь с расписанием — обратная сторона ClassSession.membership_plan
    class_sessions: Mapped[List["ClassSession"]] = relationship(
        "ClassSession",
        back_populates="membership_plan",
    )