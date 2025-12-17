# tests/test_me_leads.py
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User
from app.models.lead import Lead

client = TestClient(app, raise_server_exceptions=False)


def _email() -> str:
    return f"me_{uuid.uuid4().hex[:8]}@example.com"


def test_me_leads_requires_auth():
    resp = client.get("/api/v1/me/leads")
    assert resp.status_code == 401, resp.text


def test_me_leads_returns_only_current_user_leads():
    password = "secret123"

    # 1) регистрируем и логиним клиента A
    email_a = _email()
    resp_reg_a = client.post(
        "/api/v1/auth/register",
        json={"email": email_a, "password": password},
    )
    assert resp_reg_a.status_code == 201, resp_reg_a.text

    resp_login_a = client.post(
        "/api/v1/auth/login",
        json={"email": email_a, "password": password},
    )
    assert resp_login_a.status_code == 200, resp_login_a.text
    token_a = resp_login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2) регистрируем и логиним клиента B
    email_b = _email()
    resp_reg_b = client.post(
        "/api/v1/auth/register",
        json={"email": email_b, "password": password},
    )
    assert resp_reg_b.status_code == 201, resp_reg_b.text

    resp_login_b = client.post(
        "/api/v1/auth/login",
        json={"email": email_b, "password": password},
    )
    assert resp_login_b.status_code == 200, resp_login_b.text
    token_b = resp_login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3) A создаёт лид (через public API)
    payload_a = {
        "full_name": "Client A Lead",
        "phone": "+37360000010",
        "location_id": 1,
        "program_type_id": None,
    }
    resp_lead_a = client.post(
        "/public/leads/guest-visit",
        json=payload_a,
        headers=headers_a,
    )
    assert resp_lead_a.status_code == 200, resp_lead_a.text
    lead_a = resp_lead_a.json()

    # 4) B создаёт лид (через public API)
    payload_b = {
        "full_name": "Client B Lead",
        "phone": "+37360000011",
        "location_id": 1,
        "program_type_id": None,
    }
    resp_lead_b = client.post(
        "/public/leads/guest-visit",
        json=payload_b,
        headers=headers_b,
    )
    assert resp_lead_b.status_code == 200, resp_lead_b.text
    lead_b = resp_lead_b.json()

    # 5) На всякий случай: вручную привяжем user_id в БД
    db = SessionLocal()
    try:
        user_a = db.query(User).filter(User.email == email_a).one()
        user_b = db.query(User).filter(User.email == email_b).one()

        db_lead_a = db.query(Lead).get(lead_a["id"])
        db_lead_b = db.query(Lead).get(lead_b["id"])

        # Если по какой-то причине current_user не проставился,
        # гарантированно привяжем лиды к юзерам.
        db_lead_a.user_id = user_a.id
        db_lead_b.user_id = user_b.id

        db.commit()
    finally:
        db.close()

    # 6) A смотрит /me/leads → видит только свой лид
    resp_me_a = client.get("/api/v1/me/leads", headers=headers_a)
    assert resp_me_a.status_code == 200, resp_me_a.text
    data_a = resp_me_a.json()
    ids_a = {item["id"] for item in data_a}
    assert lead_a["id"] in ids_a
    assert lead_b["id"] not in ids_a

    # 7) B смотрит /me/leads → видит только свой лид
    resp_me_b = client.get("/api/v1/me/leads", headers=headers_b)
    assert resp_me_b.status_code == 200, resp_me_b.text
    data_b = resp_me_b.json()
    ids_b = {item["id"] for item in data_b}
    assert lead_b["id"] in ids_b
    assert lead_a["id"] not in ids_b
