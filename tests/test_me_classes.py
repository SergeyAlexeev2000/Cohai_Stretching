# tests/test_me_classes.py
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
    return f"classes_{uuid.uuid4().hex[:8]}@example.com"


def _create_user_and_login() -> tuple[User, dict[str, str]]:
    db = SessionLocal()
    try:
        email = _email()
        password = "secret123"

        # Регистрация
        resp_reg = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password},
        )
        assert resp_reg.status_code == 201, resp_reg.text

        # Логин
        resp_login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert resp_login.status_code == 200, resp_login.text
        token = resp_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Пользователь из БД
        user = db.query(User).filter(User.email == email).one()
        return user, headers
    finally:
        db.close()


def _ensure_basic_entities(db: Session) -> tuple[Location, ProgramType, Trainer, MembershipPlan]:
    """
    Создаёт простые Location, ProgramType, Trainer, MembershipPlan,
    если их нет, или берёт первые существующие.
    """
    location = db.query(Location).first()
    if location is None:
        location = Location(name="Test Location", address="Test address")
        db.add(location)
        db.commit()
        db.refresh(location)

    program_type = db.query(ProgramType).first()
    if program_type is None:
        program_type = ProgramType(
            name="Test Program",
            description="Test program",
            is_group=True,
        )
        db.add(program_type)
        db.commit()
        db.refresh(program_type)

    trainer = db.query(Trainer).first()
    if trainer is None:
        trainer = Trainer(full_name="Test Trainer", phone=None, email=None)
        db.add(trainer)
        db.commit()
        db.refresh(trainer)

    plan = db.query(MembershipPlan).first()
    if plan is None:
        plan = MembershipPlan(
            name="Test Plan",
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
        weekday=0,  # Monday, неважно
        start_time=time(10, 0),
        end_time=time(11, 0),
        capacity=20,
        is_active=True,
    )
    db.add(cs)
    db.commit()
    db.refresh(cs)
    return cs


def test_me_classes_empty_lists_when_no_attendances():
    user, headers = _create_user_and_login()

    resp = client.get("/api/v1/me/classes", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "upcoming" in data
    assert "history" in data
    assert data["upcoming"] == []
    assert data["history"] == []


def test_me_classes_upcoming_and_history_split_correctly():
    user, headers = _create_user_and_login()

    db = SessionLocal()
    try:
        cs = _create_class_session(db)

        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        before_yesterday = today - timedelta(days=2)

        # Будущее занятие: PLANNED на завтра → должно попасть в upcoming
        a_upcoming = Attendance(
            user_id=user.id,
            class_session_id=cs.id,
            membership_id=None,
            class_date=tomorrow,
            status=AttendanceStatus.PLANNED.value,
        )
        db.add(a_upcoming)

        # Прошедшее занятие: ATTENDED вчера → history
        a_past_attended = Attendance(
            user_id=user.id,
            class_session_id=cs.id,
            membership_id=None,
            class_date=yesterday,
            status=AttendanceStatus.ATTENDED.value,
        )
        db.add(a_past_attended)

        # Прошедшее занятие: PLANNED, но дата в прошлом (позавчера) → тоже history
        a_past_planned = Attendance(
            user_id=user.id,
            class_session_id=cs.id,
            membership_id=None,
            class_date=before_yesterday,
            status=AttendanceStatus.PLANNED.value,
        )
        db.add(a_past_planned)

        db.commit()

        db.refresh(a_upcoming)
        db.refresh(a_past_attended)
        db.refresh(a_past_planned)
    finally:
        db.close()

    resp = client.get("/api/v1/me/classes", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    upcoming_ids = {item["attendance_id"] for item in data["upcoming"]}
    history_ids = {item["attendance_id"] for item in data["history"]}

    assert a_upcoming.id in upcoming_ids
    assert a_past_attended.id in history_ids
    assert a_past_planned.id in history_ids

    # убеждаемся, что они не пересекаются
    assert a_upcoming.id not in history_ids
    assert a_past_attended.id not in upcoming_ids
    assert a_past_planned.id not in upcoming_ids
