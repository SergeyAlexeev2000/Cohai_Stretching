"""
Bootstrap initial database content for Cohai Stretching.

- Идемпотентен: можно запускать много раз, без дублей.
- Пишет подробный лог по каждому шагу.
- При ошибке в одном блоке показывает стек, но не падает целиком.

Запуск (из корня проекта):
    python -m app.tools.bootstrap_db
"""

from __future__ import annotations

import traceback
from typing import Any, Dict, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import engine

from app.models.location import Location
from app.models.program_type import ProgramType
from app.models.membership import MembershipPlan
from app.models.trainer import Trainer
from app.models.class_session import ClassSession
from app.models.lead import Lead

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def log(msg: str) -> None:
    """Простой логгер в stdout."""
    print(msg, flush=True)


def get_or_create(
    session: Session,
    model,
    lookup: Dict[str, Any],
    defaults: Dict[str, Any] | None = None,
) -> Tuple[Any, bool]:
    """
    Ищет объект по lookup-полям.
    Если найден — возвращает (obj, False).
    Если нет — создаёт с полями lookup + defaults, возвращает (obj, True).
    """
    stmt = select(model).filter_by(**lookup)
    obj = session.scalars(stmt).first()
    if obj is not None:
        return obj, False

    params = dict(lookup)
    if defaults:
        params.update(defaults)

    obj = model(**params)
    session.add(obj)
    return obj, True


# ---------------------------------------------------------
# DATA DEFINITIONS (строго под реальные поля моделей)
# ---------------------------------------------------------

# Location: id, name, address
LOCATION_DATA = [
    {
        "name": "Cohai Stretching — Testemițanu 3/13",
        "address": "str. Testemițanu 3/13, Chișinău",
    }
]

# ProgramType: id, name, description, is_group
PROGRAM_TYPES_DATA = [
    {
        "name": "Active Stretching",
        "description": "Активный стретчинг",
        "is_group": True,
    },
    {
        "name": "Classic Stretching",
        "description": "Классический стретчинг",
        "is_group": True,
    },
    {
        "name": "Back & Spine",
        "description": "Укрепление спины",
        "is_group": True,
    },
    {
        "name": "Female Styles",
        "description": "Женственные танцевальные стили",
        "is_group": True,
    },
    {
        "name": "Kids Stretching",
        "description": "Занятия для детей",
        "is_group": True,
    },
    {
        "name": "Men Stretching",
        "description": "Занятия для мужчин",
        "is_group": True,
    },
    # Персональные форматы
    {
        "name": "Personal Training",
        "description": "Персональные тренировки 1-на-1",
        "is_group": False,
    },
    {
        "name": "Duo Training",
        "description": "Тренировки в паре",
        "is_group": False,
    },
    {
        "name": "Trio Training",
        "description": "Тренировки в мини-группе (3 человека)",
        "is_group": False,
    },
]

# MembershipPlan: id, name, description, price, location_id
# location_id подставим программно (на основную локацию)
MEMBERSHIP_DATA = [
    {
        "name": "4 group sessions / month",
        "description": "4 групповые занятия в месяц",
        "price": 800,
    },
    {
        "name": "8 group sessions / month",
        "description": "8 групповых занятий в месяц",
        "price": 1400,
    },
    {
        "name": "12 group sessions / month",
        "description": "12 групповых занятий в месяц",
        "price": 1800,
    },
    {
        "name": "5 personal trainings",
        "description": "Пакет из 5 персональных тренировок",
        "price": 1800,
    },
    {
        "name": "10 personal trainings",
        "description": "Пакет из 10 персональных тренировок",
        "price": 3400,
    },
    {
        "name": "Trial group session",
        "description": "Пробное групповое занятие",
        "price": 200,
    },
]

# Trainer: id, full_name, phone, email
TRAINER_DATA = [
    {
        "full_name": "Anastasia Cohaniuc",
        "phone": None,
        "email": None,
    },
]


# ---------------------------------------------------------
# MAIN BOOTSTRAP LOGIC
# ---------------------------------------------------------

def bootstrap() -> None:
    log("🔧 Bootstrapping Cohai Stretching database...\n")

    created_total = 0

    with Session(engine) as session:
        # 1) LOCATIONS
        log("📍 Adding locations...")
        all_locations: list[Location] = []
        try:
            for data in LOCATION_DATA:
                lookup = {"name": data["name"]}
                defaults = {"address": data.get("address")}
                obj, created = get_or_create(session, Location, lookup, defaults)
                all_locations.append(obj)
                created_total += int(created)
                log(f"  • {obj.name}  {'(new)' if created else '(exists)'}")
        except Exception:
            log("  ❌ Error while adding locations:")
            traceback.print_exc()
        log("")

        # если не смогли создать ни одной локации — дальше нет смысла
        if not all_locations:
            log("❌ No locations in DB, aborting bootstrap.")
            return

        main_location = all_locations[0]

        # 2) PROGRAM TYPES
        log("🧘 Adding program types...")
        try:
            for data in PROGRAM_TYPES_DATA:
                lookup = {"name": data["name"]}
                defaults = {
                    "description": data.get("description"),
                    "is_group": data["is_group"],
                }
                obj, created = get_or_create(session, ProgramType, lookup, defaults)
                created_total += int(created)
                log(f"  • {obj.name}  {'(new)' if created else '(exists)'}")
        except Exception:
            log("  ❌ Error while adding program types:")
            traceback.print_exc()
        log("")

        # 3) MEMBERSHIP PLANS
        log("🧾 Adding membership plans...")
        try:
            for data in MEMBERSHIP_DATA:
                lookup = {
                    "name": data["name"],
                    "location_id": main_location.id,
                }
                defaults = {
                    "description": data.get("description"),
                    "price": data["price"],
                }
                obj, created = get_or_create(session, MembershipPlan, lookup, defaults)
                created_total += int(created)
                log(f"  • {obj.name}  {'(new)' if created else '(exists)'}")
        except Exception:
            log("  ❌ Error while adding membership plans:")
            traceback.print_exc()
        log("")

        # 4) TRAINERS
        log("🧑‍🏫 Adding trainers...")
        try:
            for data in TRAINER_DATA:
                lookup = {"full_name": data["full_name"]}
                defaults = {
                    "phone": data.get("phone"),
                    "email": data.get("email"),
                }
                obj, created = get_or_create(session, Trainer, lookup, defaults)
                created_total += int(created)
                log(f"  • {obj.full_name}  {'(new)' if created else '(exists)'}")
        except Exception:
            log("  ❌ Error while adding trainers:")
            traceback.print_exc()
        log("")

        # финальный commit — даже если были частичные ошибки,
        # всё что удалось создать, попадёт в БД
        try:
            session.commit()
        except Exception:
            log("❌ Error on session.commit():")
            traceback.print_exc()
            session.rollback()
            return

    log(f"\n🎉 DONE! Added {created_total} new records (summed over all entities).")
    log("   You can run this script multiple times — rows will not be duplicated.\n")


if __name__ == "__main__":
    bootstrap()
