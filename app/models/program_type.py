# app/models/program_type.py
from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.class_session import ClassSession
    from app.models.lead import Lead


class ProgramType(Base):
    __tablename__ = "program_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # как в таблице v0
    is_group: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ONE ProgramType -> MANY ClassSession
    class_sessions: Mapped[List["ClassSession"]] = relationship(
        "ClassSession",
        back_populates="program_type",
        cascade="all, delete-orphan",
    )

    # ONE ProgramType -> MANY Lead
    leads: Mapped[List["Lead"]] = relationship(
        "Lead",
        back_populates="program_type",
    )


__all__ = ["ProgramType"]

