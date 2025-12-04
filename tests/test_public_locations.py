# tests/test_public_locations.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_locations_status_code():
    resp = client.get("/public/locations")
    assert resp.status_code == 200


def test_list_locations_non_empty_after_bootstrap():
    """
    После bootstrap_db в БД должна быть хотя бы одна локация.
    """
    resp = client.get("/public/locations")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    first = data[0]
    # базовая структура
    assert "id" in first
    assert "name" in first
    assert "address" in first
