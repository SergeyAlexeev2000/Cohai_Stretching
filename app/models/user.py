# app/models/user.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, Integer, String, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    # только для type hints, НЕ выполняется в рантайме
    from app.models.membership import Membership
    from app.models.trainer import Trainer
    from app.models.lead import Lead

class UserRole(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    TRAINER = "TRAINER"
    CLIENT = "CLIENT"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.CLIENT,
    )
    
    # лиды, где этот пользователь — клиент
    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="user",
        foreign_keys="Lead.user_id",          # ВАЖНО
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    memberships: Mapped[list["Membership"]] = relationship(
        "Membership",
        back_populates="user",
    )
    
    trainer_profile: Mapped["Trainer | None"] = relationship(
        "Trainer",
        back_populates="user",
        uselist=False,
    )

    # лиды, за которые этот пользователь отвечает как админ
    admin_leads_assigned: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="assigned_admin",
        foreign_keys="Lead.assigned_admin_id",   # ВАЖНО
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"

__all__ = ["User", "UserRole"]
