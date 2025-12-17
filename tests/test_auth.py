# tests/test_auth.py
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app

# В остальных тестах у тебя, если помню, raise_server_exceptions=False,
# чтобы в случае ошибки видеть статус-коды, а не трейсбэк питона.
client = TestClient(app, raise_server_exceptions=True)


def _unique_email(prefix: str = "user") -> str:
    """Сгенерировать уникальный email, чтобы не конфликтовать с уже существующими."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def test_register_creates_client_user():
    email = _unique_email("client")
    payload = {
        "email": email,
        "password": "secret123",
        "full_name": "Test User",
        "phone": "+37360000000",
    }

    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert data["email"] == email
    assert data["role"] == "CLIENT"
    assert data["full_name"] == "Test User"
    assert data["phone"] == "+37360000000"
    assert "id" in data


def test_register_duplicate_email_fails():
    email = _unique_email("dup")
    payload = {
        "email": email,
        "password": "secret123",
    }

    # первый раз — ок
    resp1 = client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201, resp1.text

    # второй раз — уже должно упасть с 400
    resp2 = client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 400, resp2.text
    assert "already exists" in resp2.text


def test_login_returns_token_for_valid_credentials():
    email = _unique_email("login")
    password = "secret123"

    # сначала регистрируем пользователя
    resp_reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert resp_reg.status_code == 201, resp_reg.text

    # затем логинимся
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_fails_with_wrong_password():
    email = _unique_email("wrongpass")
    password = "secret123"

    # создаём пользователя
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )

    # пробуем залогиниться с неверным паролем
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "bad_password"},
    )

    assert resp.status_code == 401, resp.text
    assert "Incorrect email or password" in resp.text


def test_me_returns_current_user():
    email = _unique_email("me")
    password = "secret123"

    # регистрация
    resp_reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert resp_reg.status_code == 201, resp_reg.text
    user_data = resp_reg.json()
    user_id = user_data["id"]

    # логин — получаем токен
    resp_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp_login.status_code == 200, resp_login.text
    token = resp_login.json()["access_token"]

    # запрос /me с заголовком Authorization
    resp_me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp_me.status_code == 200, resp_me.text
    me_data = resp_me.json()

    assert me_data["id"] == user_id
    assert me_data["email"] == email
    assert me_data["role"] == "CLIENT"


def test_me_requires_auth():
    """Проверяем, что /auth/me без токена возвращает 401."""
    resp_me = client.get("/api/v1/auth/me")
    assert resp_me.status_code == 401, resp_me.text
