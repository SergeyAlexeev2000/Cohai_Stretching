# tests/test_public_program_types.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_program_types_status_code():
    resp = client.get("/public/program-types")
    assert resp.status_code == 200


def test_list_program_types_non_empty_after_bootstrap():
    """
    После bootstrap_db в БД должно быть несколько типов программ.
    """
    resp = client.get("/public/program-types")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "description" in first
    assert "is_group" in first
