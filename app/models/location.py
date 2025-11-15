# app/models/location.py
from __future__ import annotations

from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=True)

    # Связь с занятиями (если уже есть ClassSession)
    class_sessions: Mapped[List["ClassSession"]] = relationship(
        back_populates="location",
        cascade="all, delete-orphan",
    )
