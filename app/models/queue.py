from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class SlotHoldStatus(str, Enum):
    ACTIVE = "ACTIVE"       # место реально занято активным клиентом
    OFFERED = "OFFERED"     # место предложено очереднику, держим N минут
    EXPIRED = "EXPIRED"     # оффер протух


class SlotHold(Base):
    __tablename__ = "slot_holds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=SlotHoldStatus.ACTIVE.value)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_slot_hold_user"),
        Index("ix_slot_holds_status", "status"),
    )


class ReservationStatus(str, Enum):
    HELD = "HELD"             # бронь (таймер)
    CONFIRMED = "CONFIRMED"   # успешно оплачено/подтверждено
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"


class MembershipReservation(Base):
    __tablename__ = "membership_reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    membership_plan_id: Mapped[int] = mapped_column(
        ForeignKey("membership_plans.id", ondelete="RESTRICT"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=ReservationStatus.HELD.value)
    reserved_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_reservations_user_status", "user_id", "status"),
    )


class WaitlistStatus(str, Enum):
    WAITING = "WAITING"
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    SKIPPED = "SKIPPED"


class WaitlistEntry(Base):
    __tablename__ = "waitlist_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=WaitlistStatus.WAITING.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_waitlist_user"),
        Index("ix_waitlist_status_created", "status", "created_at"),
    )


__all__ = [
    "SlotHold",
    "SlotHoldStatus",
    "MembershipReservation",
    "ReservationStatus",
    "WaitlistEntry",
    "WaitlistStatus",
]
