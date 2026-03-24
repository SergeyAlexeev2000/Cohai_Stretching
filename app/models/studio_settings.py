# app/models/studio_settings.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class StudioSettings(Base):
    __tablename__ = "studio_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # будем держать id=1
    studio_capacity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="12")
    reservation_ttl_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="60")
    offer_ttl_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="30")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
