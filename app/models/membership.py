# app/models/membership.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.location import Location


class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    # связь с локацией
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    location: Mapped["Location"] = relationship(back_populates="membership_plans")
