#app/models/lead.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from sqlalchemy import( 
    Integer, String, Boolean,
    DateTime, ForeignKey, 
    Enum as SqlEnum,)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.user import User

from enum import Enum

if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.program_type import ProgramType
    from app.models.trainer import Trainer

def utcnow_naive() -> datetime:
    """
    Возвращает текущее UTC-время *без таймзоны* (как было раньше),
    но не вызывает deprecated datetime.utcnow().
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class LeadStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"
    DECLINED = "DECLINED"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)

    # источник лида (сайт, инста, рекомендации и т.п.)
    source: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # FK на локацию и тип программы (в v0 они nullable)
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"),
        nullable=True,
    )
    program_type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("program_types.id"),
        nullable=True,
    )

    is_processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utcnow_naive,
    )

    # ORM-связи (обратные к Location.leads / ProgramType.leads)
    location: Mapped[Optional["Location"]] = relationship(
        "Location",
        back_populates="leads",
    )
    program_type: Mapped[Optional["ProgramType"]] = relationship(
        "ProgramType",
        back_populates="leads",
    )

    user_id: Mapped[int | None] = mapped_column(
    ForeignKey("users.id"),
    nullable=True,
    )

    user: Mapped["User | None"] = relationship(
    "User",
    back_populates="leads",
    foreign_keys="Lead.user_id",          # ВАЖНО
    )

    message: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,   # ← Python-level default, ORM всегда подставит значение
    )

    # новый статус
    status: Mapped[LeadStatus] = mapped_column(
        SqlEnum(LeadStatus),
        default=LeadStatus.NEW,
        nullable=False,
    )

    # назначенный тренер
    assigned_trainer_id: Mapped[int | None] = mapped_column(
        ForeignKey("trainers.id"),
        nullable=True,
    )
    assigned_trainer: Mapped["Trainer | None"] = relationship(
        "Trainer",
        back_populates="leads_assigned",
    )

    # назначенный админ (опционально)
    assigned_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    assigned_admin: Mapped["User | None"] = relationship(
    "User",
    back_populates="admin_leads_assigned",
    foreign_keys="Lead.assigned_admin_id",    # ВАЖНО
    )


__all__ = ["Lead"]
