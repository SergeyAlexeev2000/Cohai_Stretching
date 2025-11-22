# app/models/program_type.py
from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    # только для type-checker, в рантайме не импортируется
    from app.models.class_session import ClassSession


class ProgramType(Base):
    __tablename__ = "program_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # является ли программа групповой, просто пример поля
    is_group: Mapped[bool] = mapped_column(Boolean, default=True)

    # ONE ProgramType -> MANY ClassSession
    # важно: back_populates совпадает с именем поля в ClassSession.program_type
    class_sessions: Mapped[list["ClassSession"]] = relationship(
        "ClassSession",
        back_populates="program_type",
        cascade="all, delete-orphan",
    )


__all__ = ["ProgramType"]
