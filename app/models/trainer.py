# app/models/trainer.py
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.class_session import ClassSession
    from app.models.user import User
    from app.models.lead import Lead

class Trainer(Base):
    __tablename__ = "trainers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ONE Trainer -> MANY ClassSession
    class_sessions: Mapped[List["ClassSession"]] = relationship(
        "ClassSession",
        back_populates="trainer",
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        comment="Связанный пользовательский аккаунт тренера",
    )

    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="trainer_profile",
        uselist=False,
    )

    leads_assigned: Mapped[list["Lead"]] = relationship(
    "Lead",
    back_populates="assigned_trainer",
    )

__all__ = ["Trainer"]

