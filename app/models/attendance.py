# app/models/attendance.py
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Date,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.class_session import ClassSession
    from app.models.membership import Membership


class AttendanceStatus(str, Enum):
    """
    Статус записи/посещения на занятие.
    """

    PLANNED = "PLANNED"    # записан, занятие ещё не прошло
    ATTENDED = "ATTENDED"  # был на занятии
    MISSED = "MISSED"      # был записан, но не пришёл
    CANCELED = "CANCELED"  # отменил запись


class Attendance(Base):
    """
    Конкретная запись пользователя на конкретное занятие.

    Связи:
    - user_id          → User
    - class_session_id → ClassSession
    - membership_id    → Membership (с которого списываются посещения; может быть None)
    """

    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    class_session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("class_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    membership_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("memberships.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(length=20),
        nullable=False,
        default=AttendanceStatus.PLANNED.value,
        server_default=AttendanceStatus.PLANNED.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    class_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(length=20),
        nullable=False,
        default=AttendanceStatus.PLANNED.value,
        server_default=AttendanceStatus.PLANNED.value,
    )

    # --- relationships ---

    user: Mapped["User"] = relationship(
        "User",
        backref="attendances",
    )
    class_session: Mapped["ClassSession"] = relationship(
        "ClassSession",
        backref="attendances",
    )
    membership: Mapped["Membership | None"] = relationship(
        "Membership",
        backref="attendances",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "class_session_id",
            "class_date",
            name="uq_attendance_user_session_date",
        ),
    )
