# app/models/__init__.py
"""
Единая точка импорта всех ORM-моделей.

Задачи:
- При `import app.models` загружаются все подмодули с моделями.
- SQLAlchemy видит все классы в одном registry и может разрешать
  строковые ссылки в relationship("...").

ВНИМАНИЕ: внутри отдельных файлов моделей мы НЕ импортируем друг друга
в рантайме — только через строки и TYPE_CHECKING.
"""

from .location import Location
from .location_area import LocationArea
from .program_type import ProgramType
from .trainer import Trainer
from .membership import MembershipPlan, Membership, MembershipStatus
from .class_session import ClassSession
from .lead import Lead
from .attendance import Attendance, AttendanceStatus
from .user import User, UserRole

__all__ = [
    "Location",
    "LocationArea",
    "ProgramType",
    "Trainer",
    "MembershipPlan",
    "Membership",
    "MembershipStatus",
    "ClassSession",
    "Lead",
    "Attendance",
    "AttendanceStatus",
    "User",
    "UserRole",
]
