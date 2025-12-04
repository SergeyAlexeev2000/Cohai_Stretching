# tests/test_admin_access.py
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=True)


def _email():
    return f"u_{uuid.uuid4().hex[:8]}@example.com"


def test_admin_leads_requires_auth():
    """Без токена → 401"""
    resp = client.get("/api/v1/admin/leads")
    assert resp.status_code == 401


def test_admin_leads_client_forbidden():
    """CLIENT с токеном → 403"""
    email = _email()
    password = "secret123"

    # регистрируем клиента
    reg = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert reg.status_code == 201

    # логин
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]

    # запрос в админку
    resp = client.get(
        "/api/v1/admin/leads",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 403
