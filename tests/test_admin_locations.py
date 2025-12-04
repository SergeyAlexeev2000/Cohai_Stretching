# tests/test_admin_locations.py

from fastapi.testclient import TestClient

from app.main import app

# Важно: так же, как в admin_leads / admin_memberships
client = TestClient(app, raise_server_exceptions=False)


def _create_location_via_admin(
    name: str = "Test Location",
    address: str | None = "Some address",
):
    """
    Хелпер: создаёт локацию через POST /api/v1/admin/locations
    и возвращает JSON.
    """
    payload = {
        "name": name,
        "address": address,
    }
    resp = client.post("/api/v1/admin/locations", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    return data


def test_admin_create_and_get_location():
    """
    Создаём локацию и читаем её по id.
    """
    loc = _create_location_via_admin(
        name="Admin Test Studio",
        address="Chisinau, Main street 1",
    )

    resp = client.get(f"/api/v1/admin/locations/{loc['id']}")
    assert resp.status_code == 200

    data = resp.json()
    assert data["id"] == loc["id"]
    assert data["name"] == "Admin Test Studio"
    assert data["address"] == "Chisinau, Main street 1"


def test_admin_list_locations_contains_created():
    """
    Созданная локация должна появляться в списке.
    """
    loc = _create_location_via_admin(
        name="List Studio",
        address="Addr 2",
    )

    resp = client.get("/api/v1/admin/locations")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    ids = [item["id"] for item in data]
    assert loc["id"] in ids


def test_admin_update_location_changes_name():
    """
    PATCH должен менять имя локации.
    """
    loc = _create_location_via_admin(
        name="Old Studio Name",
        address="Addr 3",
    )

    resp_patch = client.patch(
        f"/api/v1/admin/locations/{loc['id']}",
        json={"name": "New Studio Name"},
    )
    assert resp_patch.status_code == 200

    data = resp_patch.json()
    assert data["id"] == loc["id"]
    assert data["name"] == "New Studio Name"

    # проверим, что изменение действительно сохранено
    resp_get = client.get(f"/api/v1/admin/locations/{loc['id']}")
    assert resp_get.status_code == 200
    data_get = resp_get.json()
    assert data_get["name"] == "New Studio Name"


def test_admin_delete_location_then_404_on_get():
    """
    DELETE должен удалять локацию; после этого GET должен вернуть 404.
    """
    loc = _create_location_via_admin(
        name="Delete Me Studio",
        address="Addr 4",
    )

    resp_delete = client.delete(f"/api/v1/admin/locations/{loc['id']}")
    assert resp_delete.status_code == 204

    resp_get = client.get(f"/api/v1/admin/locations/{loc['id']}")
    assert resp_get.status_code == 404
