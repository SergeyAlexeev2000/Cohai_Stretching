# tests/test_admin_memberships.py

from fastapi.testclient import TestClient

from app.main import app
from tests.test_admin_leads import admin_headers

client = TestClient(app, raise_server_exceptions=False)


def _create_membership_via_admin(
    name: str = "Admin Test Tariff",
    price: float = 100.0,
    location_id: int = 1,
    description: str | None = "Test description",
):
    payload = {
        "name": name,
        "price": price,
        "location_id": location_id,
        "description": description,
    }
    resp = client.post(
        "/api/v1/admin/memberships",
        json=payload,
        headers=admin_headers(),
    )
    assert resp.status_code == 201
    return resp.json()


def test_admin_create_and_get_membership():
    membership = _create_membership_via_admin(
        name="Admin Created Tariff",
        price=150.0,
    )

    resp = client.get(
        f"/api/v1/admin/memberships/{membership['id']}",
        headers=admin_headers(),
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["id"] == membership["id"]
    assert data["name"] == "Admin Created Tariff"
    assert data["price"] == 150.0
    assert data["location_id"] == 1


def test_admin_list_memberships_contains_created():
    membership = _create_membership_via_admin(
        name="List Visible Tariff",
        price=200.0,
    )

    resp = client.get("/api/v1/admin/memberships", headers=admin_headers())
    assert resp.status_code == 200

    data = resp.json()
    ids = [item["id"] for item in data]
    assert membership["id"] in ids


def test_admin_update_membership_changes_name():
    membership = _create_membership_via_admin(
        name="Old Name Tariff",
        price=250.0,
    )

    resp_patch = client.patch(
        f"/api/v1/admin/memberships/{membership['id']}",
        json={"name": "New Name Tariff"},
        headers=admin_headers(),     # ← ЭТО ВАЖНО
    )
    assert resp_patch.status_code == 200

    data = resp_patch.json()
    assert data["id"] == membership["id"]
    assert data["name"] == "New Name Tariff"

    resp_get = client.get(
        f"/api/v1/admin/memberships/{membership['id']}",
        headers=admin_headers(),
    )
    assert resp_get.status_code == 200
    data_get = resp_get.json()
    assert data_get["name"] == "New Name Tariff"


def test_admin_delete_membership_then_404_on_get():
    membership = _create_membership_via_admin(
        name="Delete Me Tariff",
        price=300.0,
    )

    resp_delete = client.delete(
        f"/api/v1/admin/memberships/{membership['id']}",
        headers=admin_headers(),     # ← ЭТО ВАЖНО
    )
    assert resp_delete.status_code == 204

    resp_get = client.get(
        f"/api/v1/admin/memberships/{membership['id']}",
        headers=admin_headers(),
    )
    assert resp_get.status_code == 404
