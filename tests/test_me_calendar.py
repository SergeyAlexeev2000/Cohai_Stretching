# tests/test_me_calendar.py
from __future__ import annotations

from datetime import date, timedelta, time
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User
from app.models.location import Location
from app.models.program_type import ProgramType
from app.models.trainer import Trainer
from app.models.membership import MembershipPlan
from app.models.class_session import ClassSession
from app.models.attendance import Attendance, AttendanceStatus

client = TestClient(app, raise_server_exceptions=False)


def _email() -> str:
    return f"calendar_{uuid.uuid4().hex[:8]}@example.com"


def _create_user_and_login() -> tuple[User, dict[str, str]]:
    db = SessionLocal()
    try:
        email = _email()
        password = "secret123"

        resp_reg = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password},
        )
        assert resp_reg.status_code == 201, resp_reg.text

        resp_login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert resp_login.status_code == 200, resp_login.text
        token = resp_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        user = db.query(User).filter(User.email == email).one()
        return user, headers
    finally:
        db.close()


def _ensure_basic_entities(db: Session) -> tuple[Location, ProgramType, Trainer, MembershipPlan]:
    location = db.query(Location).first()
    if location is None:
        location = Location(name="CalTest Location", address="Test address")
        db.add(location)
        db.commit()
        db.refresh(location)

    program_type = db.query(ProgramType).first()
    if program_type is None:
        program_type = ProgramType(
            name="CalTest Program",
            description="Test program",
            is_group=True,
        )
        db.add(program_type)
        db.commit()
        db.refresh(program_type)

    trainer = db.query(Trainer).first()
    if trainer is None:
        trainer = Trainer(full_name="CalTest Trainer", phone=None, email=None)
        db.add(trainer)
        db.commit()
        db.refresh(trainer)

    plan = db.query(MembershipPlan).first()
    if plan is None:
        plan = MembershipPlan(
            name="CalTest Plan",
            description="Test plan",
            price=1000,
            location_id=location.id,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

    return location, program_type, trainer, plan


def _create_class_session(db: Session) -> ClassSession:
    location, program_type, trainer, plan = _ensure_basic_entities(db)

    cs = ClassSession(
        location_id=location.id,
        program_type_id=program_type.id,
        trainer_id=trainer.id,
        membership_plan_id=plan.id,
        weekday=0,
        start_time=time(10, 0),
        end_time=time(11, 0),
        capacity=20,
        is_active=True,
    )
    db.add(cs)
    db.commit()
    db.refresh(cs)
    return cs


def test_me_calendar_empty_when_no_attendances():
    user, headers = _create_user_and_login()

    resp = client.get(
        "/api/v1/me/calendar",
        headers=headers,
        params={"start_date": "2025-01-01", "end_date": "2025-01-31"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["start_date"] == "2025-01-01"
    assert data["end_date"] == "2025-01-31"
    assert data["days"] == []


def test_me_calendar_groups_by_date_and_filters_range():
    user, headers = _create_user_and_login()

    db = SessionLocal()
    try:
        # два разных занятия (например, два слота в один день)
        cs1 = _create_class_session(db)
        cs2 = _create_class_session(db)

        d1 = date(2025, 11, 27)
        d2 = date(2025, 11, 28)
        d_outside = date(2025, 12, 1)

        # Занятие на 27-е: PLANNED (cs1)
        a1 = Attendance(
            user_id=user.id,
            class_session_id=cs1.id,
            membership_id=None,
            class_date=d1,
            status=AttendanceStatus.PLANNED.value,
        )
        db.add(a1)

        # Второе занятие в тот же день, но другой класс (cs2)
        a2 = Attendance(
            user_id=user.id,
            class_session_id=cs2.id,
            membership_id=None,
            class_date=d1,
            status=AttendanceStatus.ATTENDED.value,
        )
        db.add(a2)

        # Занятие на 28-е (cs1)
        a3 = Attendance(
            user_id=user.id,
            class_session_id=cs1.id,
            membership_id=None,
            class_date=d2,
            status=AttendanceStatus.MISSED.value,
        )
        db.add(a3)

        # Занятие вне диапазона (cs1)
        a_out = Attendance(
            user_id=user.id,
            class_session_id=cs1.id,
            membership_id=None,
            class_date=d_outside,
            status=AttendanceStatus.PLANNED.value,
        )
        db.add(a_out)

        db.commit()

        db.refresh(a1)
        db.refresh(a2)
        db.refresh(a3)
        db.refresh(a_out)
    finally:
        db.close()

    resp = client.get(
        "/api/v1/me/calendar",
        headers=headers,
        params={"start_date": "2025-11-27", "end_date": "2025-11-28"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["start_date"] == "2025-11-27"
    assert data["end_date"] == "2025-11-28"

    days = {d["date"]: d for d in data["days"]}

    # Должны быть два дня: 27 и 28
    assert "2025-11-27" in days
    assert "2025-11-28" in days

    classes_27 = days["2025-11-27"]["classes"]
    classes_28 = days["2025-11-28"]["classes"]

    ids_27 = {c["attendance_id"] for c in classes_27}
    ids_28 = {c["attendance_id"] for c in classes_28}

    assert a1.id in ids_27
    assert a2.id in ids_27
    assert a3.id in ids_28

    # А вот запись вне диапазона не должна попасть никуда
    assert a_out.id not in ids_27
    assert a_out.id not in ids_28

