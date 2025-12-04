# tests/test_admin_memberships.py

from fastapi.testclient import TestClient

from app.main import app

# ВАЖНО: не пробрасываем AppError наружу, а получаем HTTP-ответ 404
client = TestClient(app, raise_server_exceptions=False)


def _create_membership_via_admin(
    name: str = "Admin Test Tariff",
    price: float = 100.0,
    location_id: int = 1,
    description: str | None = "Test description",
):
    """
    Хелпер: создаёт тариф через админский POST /api/v1/admin/memberships
    и возвращает JSON.
    """
    payload = {
        "name": name,
        "price": price,
        "location_id": location_id,
        "description": description,
    }
    resp = client.post("/api/v1/admin/memberships", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    return data


def test_admin_create_and_get_membership():
    """
    Создаём тариф через админку и сразу читаем его по id.
    """
    membership = _create_membership_via_admin(
        name="Admin Created Tariff",
        price=150.0,
    )

    resp = client.get(f"/api/v1/admin/memberships/{membership['id']}")
    assert resp.status_code == 200

    data = resp.json()
    assert data["id"] == membership["id"]
    assert data["name"] == "Admin Created Tariff"
    assert data["price"] == 150.0
    assert data["location_id"] == 1


def test_admin_list_memberships_contains_created():
    """
    Созданный тариф должен появляться в списке /api/v1/admin/memberships.
    """
    membership = _create_membership_via_admin(
        name="List Visible Tariff",
        price=200.0,
    )

    resp = client.get("/api/v1/admin/memberships")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    assert membership["id"] in ids


def test_admin_update_membership_changes_name():
    """
    PATCH /api/v1/admin/memberships/{id} должен менять имя тарифа.
    """
    membership = _create_membership_via_admin(
        name="Old Name Tariff",
        price=250.0,
    )

    resp_patch = client.patch(
        f"/api/v1/admin/memberships/{membership['id']}",
        json={"name": "New Name Tariff"},
    )
    assert resp_patch.status_code == 200

    data = resp_patch.json()
    assert data["id"] == membership["id"]
    assert data["name"] == "New Name Tariff"

    # проверим, что изменение сохранилось
    resp_get = client.get(f"/api/v1/admin/memberships/{membership['id']}")
    assert resp_get.status_code == 200
    data_get = resp_get.json()
    assert data_get["name"] == "New Name Tariff"


def test_admin_delete_membership_then_404_on_get():
    """
    DELETE /api/v1/admin/memberships/{id} должен удалять тариф.
    После этого GET по этому id должен вернуть 404.
    """
    membership = _create_membership_via_admin(
        name="Delete Me Tariff",
        price=300.0,
    )

    resp_delete = client.delete(
        f"/api/v1/admin/memberships/{membership['id']}"
    )
    assert resp_delete.status_code == 204

    resp_get = client.get(
        f"/api/v1/admin/memberships/{membership['id']}"
    )
    assert resp_get.status_code == 404
