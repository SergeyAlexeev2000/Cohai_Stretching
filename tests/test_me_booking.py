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
    return f"booking_{uuid.uuid4().hex[:8]}@example.com"


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
        location = Location(name="BookTest Location", address="Test address")
        db.add(location)
        db.commit()
        db.refresh(location)

    program_type = db.query(ProgramType).first()
    if program_type is None:
        program_type = ProgramType(
            name="BookTest Program",
            description="Test program",
            is_group=True,
        )
        db.add(program_type)
        db.commit()
        db.refresh(program_type)

    trainer = db.query(Trainer).first()
    if trainer is None:
        trainer = Trainer(full_name="BookTest Trainer", phone=None, email=None)
        db.add(trainer)
        db.commit()
        db.refresh(trainer)

    plan = db.query(MembershipPlan).first()
    if plan is None:
        plan = MembershipPlan(
            name="BookTest Plan",
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
        weekday=0,  # Monday
        start_time=time(10, 0),
        end_time=time(11, 0),
        capacity=2,
        is_active=True,
    )
    db.add(cs)
    db.commit()
    db.refresh(cs)
    return cs


def _next_weekday(target_weekday: int) -> date:
    """
    Найти ближайшую (включая сегодня) дату с данным weekday (0=Monday,...,6=Sunday).
    """
    today = date.today()
    delta = (target_weekday - today.weekday()) % 7
    return today + timedelta(days=delta)


def test_book_class_creates_attendance_and_shows_in_upcoming():
    user, headers = _create_user_and_login()

    db = SessionLocal()
    try:
        cs = _create_class_session(db)
    finally:
        db.close()

    class_date = _next_weekday(cs.weekday)

    resp = client.post(
        "/api/v1/me/classes/book",
        headers=headers,
        json={
            "class_session_id": cs.id,
            "class_date": class_date.isoformat(),
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    attendance_id = data["attendance_id"]
    assert data["class_session_id"] == cs.id
    assert data["class_date"] == class_date.isoformat()
    assert data["status"] == AttendanceStatus.PLANNED.value

    # Проверяем, что попало в upcoming
    resp_me = client.get("/api/v1/me/classes", headers=headers)
    assert resp_me.status_code == 200
    classes_data = resp_me.json()
    upcoming_ids = {item["attendance_id"] for item in classes_data["upcoming"]}
    assert attendance_id in upcoming_ids


def test_double_booking_same_class_and_date_forbidden():
    user, headers = _create_user_and_login()

    db = SessionLocal()
    try:
        cs = _create_class_session(db)
    finally:
        db.close()

    class_date = _next_weekday(cs.weekday)

    payload = {
        "class_session_id": cs.id,
        "class_date": class_date.isoformat(),
    }

    resp1 = client.post("/api/v1/me/classes/book", headers=headers, json=payload)
    assert resp1.status_code == 200, resp1.text

    resp2 = client.post("/api/v1/me/classes/book", headers=headers, json=payload)
    assert resp2.status_code == 400, resp2.text
    assert "already booked" in resp2.text or "already" in resp2.text.lower()


def test_cancel_moves_from_upcoming_to_history():
    user, headers = _create_user_and_login()

    db = SessionLocal()
    try:
        cs = _create_class_session(db)
    finally:
        db.close()

    class_date = _next_weekday(cs.weekday)

    # бронируем
    resp_book = client.post(
        "/api/v1/me/classes/book",
        headers=headers,
        json={"class_session_id": cs.id, "class_date": class_date.isoformat()},
    )
    assert resp_book.status_code == 200, resp_book.text
    booked = resp_book.json()
    attendance_id = booked["attendance_id"]

    # отменяем
    resp_cancel = client.post(
        "/api/v1/me/classes/cancel",
        headers=headers,
        json={"attendance_id": attendance_id},
    )
    assert resp_cancel.status_code == 200, resp_cancel.text
    canceled = resp_cancel.json()
    assert canceled["attendance_id"] == attendance_id
    assert canceled["status"] == AttendanceStatus.CANCELED.value

    # проверяем списки
    resp_me = client.get("/api/v1/me/classes", headers=headers)
    assert resp_me.status_code == 200
    data = resp_me.json()
    upcoming_ids = {item["attendance_id"] for item in data["upcoming"]}
    history_ids = {item["attendance_id"] for item in data["history"]}

    assert attendance_id not in upcoming_ids
    assert attendance_id in history_ids


def test_cannot_cancel_other_users_attendance():
    # user1 бронирует
    user1, headers1 = _create_user_and_login()
    db = SessionLocal()
    try:
        cs = _create_class_session(db)
    finally:
        db.close()

    class_date = _next_weekday(cs.weekday)

    resp_book = client.post(
        "/api/v1/me/classes/book",
        headers=headers1,
        json={"class_session_id": cs.id, "class_date": class_date.isoformat()},
    )
    assert resp_book.status_code == 200, resp_book.text
    attendance_id = resp_book.json()["attendance_id"]

    # user2 пытается отменить
    user2, headers2 = _create_user_and_login()

    resp_cancel = client.post(
        "/api/v1/me/classes/cancel",
        headers=headers2,
        json={"attendance_id": attendance_id},
    )
    # мы отвечаем 404, чтобы не раскрывать чужие записи
    assert resp_cancel.status_code == 404, resp_cancel.text
