# app/models/program_type.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProgramType(Base):
    __tablename__ = "program_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # является ли программа групповой, просто пример поля
    is_group: Mapped[bool] = mapped_column(Boolean, default=True)