from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)

    # Источник лида (сайт, Инста и т.п.)
    source: Mapped[str | None] = mapped_column(String, nullable=True)

    # Привязка к локации и типу программы (можно оставить nullable на старте)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    program_type_id: Mapped[int | None] = mapped_column(ForeignKey("program_types.id"), nullable=True)

    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
