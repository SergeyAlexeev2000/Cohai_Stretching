# tests/test_me_profile.py
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def _email() -> str:
    return f"profile_{uuid.uuid4().hex[:8]}@example.com"


def test_get_profile_returns_current_user_data():
    password = "secret123"
    email = _email()

    # Регистрируем и логинимся
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

    # Запрашиваем профиль
    resp_profile = client.get("/api/v1/me/profile", headers=headers)
    assert resp_profile.status_code == 200, resp_profile.text

    data = resp_profile.json()
    assert data["email"] == email
    assert data["role"] == "CLIENT"  # по умолчанию при регистрации
    # full_name и phone могут быть None
    assert "full_name" in data
    assert "phone" in data


def test_patch_profile_updates_full_name_and_phone():
    password = "secret123"
    email = _email()

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

    # Обновляем профиль
    payload = {
        "full_name": "New Name",
        "phone": "+37360001234",
    }
    resp_patch = client.patch("/api/v1/me/profile", json=payload, headers=headers)
    assert resp_patch.status_code == 200, resp_patch.text

    data = resp_patch.json()
    assert data["full_name"] == "New Name"
    assert data["phone"] == "+37360001234"

    # Проверим, что GET /me/profile отдаёт те же данные
    resp_profile = client.get("/api/v1/me/profile", headers=headers)
    assert resp_profile.status_code == 200, resp_profile.text
    data2 = resp_profile.json()
    assert data2["full_name"] == "New Name"
    assert data2["phone"] == "+37360001234"


def test_patch_profile_changes_password_and_allows_login_with_new_password():
    old_password = "oldsecret123"
    new_password = "newsecret456"
    email = _email()

    # Регистрируем с старым паролем
    resp_reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": old_password},
    )
    assert resp_reg.status_code == 201, resp_reg.text

    # Логинимся старым паролем
    resp_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": old_password},
    )
    assert resp_login.status_code == 200, resp_login.text
    token = resp_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Меняем пароль через /me/profile
    payload = {
        "current_password": old_password,
        "new_password": new_password,
    }
    resp_patch = client.patch("/api/v1/me/profile", json=payload, headers=headers)
    assert resp_patch.status_code == 200, resp_patch.text

    # Логин старым паролем теперь должен провалиться
    resp_old_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": old_password},
    )
    assert resp_old_login.status_code == 401

    # Логин новым паролем должен пройти
    resp_new_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": new_password},
    )
    assert resp_new_login.status_code == 200, resp_new_login.text
