# tests/test_me_memberships.py
from __future__ import annotations

from datetime import date, timedelta
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User
from app.models.membership import Membership, MembershipStatus, MembershipPlan

client = TestClient(app, raise_server_exceptions=False)


def _email() -> str:
    return f"member_{uuid.uuid4().hex[:8]}@example.com"


def _create_user_and_login() -> tuple[User, dict[str, str]]:
    """
    Регистрирует нового пользователя, логинит его и возвращает (User, headers).
    """
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

        # Получаем пользователя из БД
        user = db.query(User).filter(User.email == email).one()
        return user, headers
    finally:
        db.close()


def _get_any_membership_plan(db: Session) -> MembershipPlan:
    """
    Возвращает любой существующий MembershipPlan из БД.

    Предполагается, что базовые планы уже есть (как в остальных тестах).
    """
    plan = db.query(MembershipPlan).first()
    assert plan is not None, "Не найден ни один MembershipPlan в БД"
    return plan


def test_me_memberships_empty_lists_when_no_memberships():
    user, headers = _create_user_and_login()

    resp = client.get("/api/v1/me/memberships", headers=headers)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert "active" in data
    assert "history" in data
    assert data["active"] == []
    assert data["history"] == []


def test_me_memberships_returns_active_and_history():
    # Создаём пользователя A
    user_a, headers_a = _create_user_and_login()

    # Создаём второго пользователя B (для проверки изоляции)
    user_b, headers_b = _create_user_and_login()

    db = SessionLocal()
    try:
        plan = _get_any_membership_plan(db)

        today = date.today()

        # Активный абонемент для A: сегодня -> +10 дней, ACTIVE
        m_active = Membership(
            user_id=user_a.id,
            membership_plan_id=plan.id,
            start_date=today,
            end_date=today + timedelta(days=10),
            visits_total=8,
            visits_used=1,
            status=MembershipStatus.ACTIVE.value,
        )
        db.add(m_active)

        # Исторический абонемент для A: завершился вчера, статус EXPIRED
        m_expired = Membership(
            user_id=user_a.id,
            membership_plan_id=plan.id,
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=1),
            visits_total=8,
            visits_used=8,
            status=MembershipStatus.EXPIRED.value,
        )
        db.add(m_expired)

        # Активный абонемент для B (не должен попадать к A)
        m_other_user = Membership(
            user_id=user_b.id,
            membership_plan_id=plan.id,
            start_date=today,
            end_date=today + timedelta(days=5),
            visits_total=None,
            visits_used=0,
            status=MembershipStatus.ACTIVE.value,
        )
        db.add(m_other_user)

        db.commit()

        # Обновим объекты с id
        db.refresh(m_active)
        db.refresh(m_expired)
        db.refresh(m_other_user)
    finally:
        db.close()

    # Запрашиваем абонементы A
    resp_a = client.get("/api/v1/me/memberships", headers=headers_a)
    assert resp_a.status_code == 200, resp_a.text
    data_a = resp_a.json()

    active_ids = {m["id"] for m in data_a["active"]}
    history_ids = {m["id"] for m in data_a["history"]}

    assert m_active.id in active_ids
    assert m_expired.id not in active_ids

    assert m_expired.id in history_ids
    assert m_active.id not in history_ids

    # Убеждаемся, что абонемент B не виден A
    assert m_other_user.id not in active_ids
    assert m_other_user.id not in history_ids

    # На всякий случай проверим, что B видит только свой
    resp_b = client.get("/api/v1/me/memberships", headers=headers_b)
    assert resp_b.status_code == 200, resp_b.text
    data_b = resp_b.json()
    active_ids_b = {m["id"] for m in data_b["active"]}
    history_ids_b = {m["id"] for m in data_b["history"]}

    assert m_other_user.id in active_ids_b or m_other_user.id in history_ids_b
    assert m_active.id not in active_ids_b
    assert m_expired.id not in history_ids_b
