# tests/test_admin_leads.py
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User, UserRole

client = TestClient(app, raise_server_exceptions=False)


def create_admin_and_get_token() -> str:
    """Создать пользователя, повысить до ADMIN и вернуть access_token."""
    email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    password = "secret123"

    # 1) регистрируем обычного клиента
    resp_reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert resp_reg.status_code == 201, resp_reg.text

    # 2) поднимаем роль до ADMIN напрямую в БД
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).one()
        user.role = UserRole.ADMIN
        db.commit()
    finally:
        db.close()

    # 3) логинимся как админ
    resp_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp_login.status_code == 200, resp_login.text

    token = resp_login.json()["access_token"]
    return token


def admin_headers() -> dict[str, str]:
    token = create_admin_and_get_token()
    return {"Authorization": f"Bearer {token}"}


def _create_test_lead(full_name: str, phone: str, location_id: int = 1):
    """
    Хелпер: создаёт лида через публичный эндпоинт
    /public/leads/guest-visit и возвращает JSON.
    """
    payload = {
        "full_name": full_name,
        "phone": phone,
        "location_id": location_id,
        "program_type_id": None,
    }
    resp = client.post("/public/leads/guest-visit", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "id" in data
    return data


def test_admin_list_leads_contains_created_lead():
    """
    После создания лида через публичный API он должен быть виден
    в админском списке /api/v1/admin/leads.
    """
    token_headers = admin_headers()
    lead = _create_test_lead("Admin Test Lead", "+37360000000")

    resp = client.get("/api/v1/admin/leads", headers=token_headers)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert isinstance(data, list)

    ids = [item["id"] for item in data]
    assert lead["id"] in ids


def test_admin_get_lead_by_id():
    """
    Проверяем эндпоинт GET /api/v1/admin/leads/{id}.
    """
    token_headers = admin_headers()
    lead = _create_test_lead("GetById Lead", "+37360000001")

    resp = client.get(
        f"/api/v1/admin/leads/{lead['id']}",
        headers=token_headers,
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["id"] == lead["id"]
    assert data["full_name"] == "GetById Lead"
    assert data["phone"] == "+37360000001"
    # базовые поля
    assert "created_at" in data
    assert "is_processed" in data


def test_admin_process_lead_marks_is_processed_true():
    """
    PATCH /api/v1/admin/leads/{id}/process должен пометить лид как обработанный.
    """
    token_headers = admin_headers()
    lead = _create_test_lead("Process Me", "+37360000002")

    # до обработки лид должен быть is_processed == False
    resp_before = client.get(
        f"/api/v1/admin/leads/{lead['id']}",
        headers=token_headers,
    )
    assert resp_before.status_code == 200, resp_before.text
    data_before = resp_before.json()
    assert data_before["is_processed"] is False

    # вызываем PATCH /process
    resp = client.patch(
        f"/api/v1/admin/leads/{lead['id']}/process",
        headers=token_headers,
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["id"] == lead["id"]
    assert data["is_processed"] is True

    # и в списке с фильтром is_processed=true он тоже должен быть
    resp_list = client.get(
        "/api/v1/admin/leads",
        params={"is_processed": True},
        headers=token_headers,
    )
    assert resp_list.status_code == 200, resp_list.text
    list_data = resp_list.json()
    ids = [item["id"] for item in list_data]
    assert lead["id"] in ids


def test_admin_list_leads_filter_by_is_processed_false():
    """
    Фильтр is_processed=false должен отдавать необработанные лиды.
    """
    token_headers = admin_headers()
    lead = _create_test_lead("Unprocessed Lead", "+37360000003")

    resp = client.get(
        "/api/v1/admin/leads",
        params={"is_processed": False},
        headers=token_headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)

    ids = [item["id"] for item in data]
    assert lead["id"] in ids


def test_admin_list_leads_filter_by_query():
    """
    Фильтр q должен искать по имени/телефону (подстроке).
    """
    token_headers = admin_headers()

    lead1 = _create_test_lead("Query Target", "+37390000001")
    lead2 = _create_test_lead("Other Lead", "+37390000002")

    # Ищем по уникальному кусочку телефона первого лида
    resp = client.get(
        "/api/v1/admin/leads",
        params={"q": "90000001"},
        headers=token_headers,
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    ids = {item["id"] for item in data}
    assert lead1["id"] in ids
    assert lead2["id"] not in ids


def test_admin_delete_lead_then_404_on_get():
    """
    DELETE /api/v1/admin/leads/{id} должен удалять лида.
    После этого GET по этому id должен вернуть 404.
    """
    token_headers = admin_headers()
    lead = _create_test_lead("Delete Me", "+37360000004")

    resp_delete = client.delete(
        f"/api/v1/admin/leads/{lead['id']}",
        headers=token_headers,
    )
    assert resp_delete.status_code == 204, resp_delete.text

    resp_get = client.get(
        f"/api/v1/admin/leads/{lead['id']}",
        headers=token_headers,
    )
    assert resp_get.status_code == 404, resp_get.text
