# app/models/trainer.py
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.class_session import ClassSession


class Trainer(Base):
    __tablename__ = "trainers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    class_sessions: Mapped[List["ClassSession"]] = relationship(
        "ClassSession",
        back_populates="trainer",
    )


__all__ = ["Trainer"]


