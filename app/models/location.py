# app/models/location.py
from __future__ import annotations

from typing import List, TYPE_CHECKING, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.class_session import ClassSession
    from app.models.membership import MembershipPlan
    from app.models.lead import Lead
    from app.models.location_area import LocationArea


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    # ONE Location -> MANY LocationArea
    areas: Mapped[List["LocationArea"]] = relationship(
        "LocationArea",
        back_populates="location",
        cascade="all, delete-orphan",
    )

    # ONE Location -> MANY ClassSession
    class_sessions: Mapped[List["ClassSession"]] = relationship(
        "ClassSession",
        back_populates="location",
        cascade="all, delete-orphan",
    )

    # ONE Location -> MANY MembershipPlan
    membership_plans: Mapped[List["MembershipPlan"]] = relationship(
        "MembershipPlan",
        back_populates="location",
        cascade="all, delete-orphan",
    )

    # ONE Location -> MANY Lead
    leads: Mapped[List["Lead"]] = relationship(
        "Lead",
        back_populates="location",
    )


__all__ = ["Location"]
