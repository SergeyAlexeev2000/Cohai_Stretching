# app/tools/bootstrap_db.py

"""
Заполнение SQLite тестовыми данными для разработки.
Запускать из корня проекта:

    ./.venv/Scripts/python app/tools/bootstrap_db.py
"""

from __future__ import annotations

# ===== A. Фиксируем sys.path, чтобы `import app` всегда работал =====
import sys
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[2]  # app/tools/bootstrap_db.py -> корень

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ===== B. Остальной код =====

from datetime import datetime, timedelta

from app.db.base import Base
from app.db.session import engine, SessionLocal

from app.models.location import Location
from app.models.program_type import ProgramType
from app.models.membership import MembershipPlan
from app.models.trainer import Trainer
from app.models.class_session import ClassSession


def reset_and_create_tables() -> None:
    """На всякий случай создаём таблицы (без дропа)."""
    Base.metadata.create_all(bind=engine)


def is_already_bootstrapped(session) -> bool:
    """Проверяем, есть ли уже какие-то данные (по локациям)."""
    return session.query(Location).count() > 0


def bootstrap_data() -> None:
    db = SessionLocal()
    try:
        if is_already_bootstrapped(db):
            print("⚠ DB already has data, nothing to do.")
            return

        print("▶ Inserting test data into SQLite…")

        # --- LOCATIONS ---
        loc_center = Location(
            name="Cohai Center",
            address="Main Street 1",
            # если в модели Location НЕТ поля city – убери эту строку
            # city="Chisinau",
        )
        loc_west = Location(
            name="Cohai West",
            address="West Avenue 21",
            # city="Chisinau",
        )
        db.add_all([loc_center, loc_west])
        db.flush()  # чтобы появились id

        # --- PROGRAM TYPES ---
        prog_group = ProgramType(
            name="Group Stretching",
            description="Group stretching class for 8–10 people.",
        )
        prog_personal = ProgramType(
            name="Personal Stretching",
            description="1-on-1 personal stretching session.",
        )
        db.add_all([prog_group, prog_personal])
        db.flush()

        # --- MEMBERSHIP PLANS ---
        m1 = MembershipPlan(
            name="Trial Week",
            description="Unlimited group classes for 7 days.",
            price=25,
            duration_days=7,
            location_id=loc_center.id,
        )
        m2 = MembershipPlan(
            name="Monthly Unlimited",
            description="Unlimited group classes for 30 days.",
            price=90,
            duration_days=30,
            location_id=loc_center.id,
        )
        m3 = MembershipPlan(
            name="10 Personal Sessions",
            description="Pack of 10 personal stretching sessions.",
            price=300,
            duration_days=90,
            location_id=loc_west.id,
        )
        db.add_all([m1, m2, m3])
        db.flush()

        # --- TRAINERS ---
        t1 = Trainer(
            full_name="Anna",
            phone=None,
            email=None,
        )
        t2 = Trainer(
            full_name="Dmitry",
            phone=None,
            email=None,
        )
        db.add_all([t1, t2])
        db.flush()

        # --- CLASS SESSIONS / SCHEDULE ---
        now = datetime.now().replace(minute=0, second=0, microsecond=0)

        s1 = ClassSession(
            location_id=loc_center.id,
            program_type_id=prog_group.id,
            trainer_id=t1.id,
            starts_at=now + timedelta(days=1, hours=10),
            ends_at=now + timedelta(days=1, hours=11),
            weekday=1,
            start_time=(now + timedelta(hours=10)).time(),
            end_time=(now + timedelta(hours=11)).time(),
            capacity=10,
            is_active=True,
        )
        s2 = ClassSession(
            location_id=loc_center.id,
            program_type_id=prog_group.id,
            trainer_id=t2.id,
            starts_at=now + timedelta(days=1, hours=18),
            ends_at=now + timedelta(days=1, hours=19),
            weekday=1,
            start_time=(now + timedelta(hours=18)).time(),
            end_time=(now + timedelta(hours=19)).time(),
            capacity=10,
            is_active=True,
        )
        s3 = ClassSession(
            location_id=loc_west.id,
            program_type_id=prog_personal.id,
            trainer_id=t1.id,
            starts_at=now + timedelta(days=2, hours=12),
            ends_at=now + timedelta(days=2, hours=13),
            weekday=2,
            start_time=(now + timedelta(hours=12)).time(),
            end_time=(now + timedelta(hours=13)).time(),
            capacity=1,
            is_active=True,
        )

        db.add_all([s1, s2, s3])

        db.commit()
        print("✅ Test data inserted successfully.")
    except Exception as e:
        db.rollback()
        print("❌ Error while bootstrapping DB:", e)
        raise
    finally:
        db.close()


def main() -> None:
    reset_and_create_tables()
    bootstrap_data()


if __name__ == "__main__":
    main()
