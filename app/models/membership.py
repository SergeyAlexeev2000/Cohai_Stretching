# app/models/membership.py
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Date,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.class_session import ClassSession
    from app.models.user import User


# ---------- Тариф (тип абонемента) ----------


class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    # как в таблице v0
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"),
        nullable=False,
    )

    location: Mapped["Location"] = relationship(
        "Location",
        back_populates="membership_plans",
    )

    # ONE MembershipPlan -> MANY ClassSession
    class_sessions: Mapped[List["ClassSession"]] = relationship(
        "ClassSession",
        back_populates="membership_plan",
    )

    # ONE MembershipPlan -> MANY Membership (конкретные абонементы пользователей)
    memberships: Mapped[List["Membership"]] = relationship(
        "Membership",
        back_populates="plan",
    )


# ---------- Конкретный абонемент пользователя ----------


class MembershipStatus(str, Enum):
    """Статус конкретного абонемента пользователя."""

    ACTIVE = "ACTIVE"      # действует, можно ходить
    EXPIRED = "EXPIRED"    # истёк по сроку
    FROZEN = "FROZEN"      # заморожен (на будущее, если захотим)
    CANCELED = "CANCELED"  # отменён / аннулирован


class Membership(Base):
    """
    Конкретный абонемент пользователя, привязанный к плану (MembershipPlan).

    Примеры:
    - "8 занятий / месяц в Локации X, с 1 по 30 число" (visits_total=8)
    - "Безлимит на 1 месяц" (visits_total=None)
    """

    __tablename__ = "memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Кому принадлежит абонемент
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user: Mapped["User"] = relationship("User", back_populates="memberships")

    # На каком плане основан
    membership_plan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("membership_plans.id", ondelete="RESTRICT"),
        nullable=False,
    )
    plan: Mapped["MembershipPlan"] = relationship("MembershipPlan", back_populates="memberships")

    # Период действия абонемента
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Посещения
    visits_total: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,         # None = "безлимит" (по времени)
    )
    visits_used: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Текущий статус
    status: Mapped[str] = mapped_column(
        String(length=20),
        nullable=False,
        default=MembershipStatus.ACTIVE.value,
        server_default=MembershipStatus.ACTIVE.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


__all__ = ["MembershipPlan", "Membership", "MembershipStatus"]
