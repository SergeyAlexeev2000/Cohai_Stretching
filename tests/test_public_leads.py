# tests/test_public_leads.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_guest_visit_status_code():
    payload = {
        "full_name": "Test Guest",
        "phone": "+37300000000",
        "location_id": 1,
        "program_type_id": None,
    }
    resp = client.post("/public/leads/guest-visit", json=payload)
    assert resp.status_code == 200


def test_create_guest_visit_response_shape():
    payload = {
        "full_name": "Another Guest",
        "phone": "+37311111111",
        "location_id": 1,
        "program_type_id": None,
    }
    resp = client.post("/public/leads/guest-visit", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    # здесь подстраиваемся под LeadRead
    assert "id" in data
    assert data["full_name"] == payload["full_name"]
    assert data["phone"] == payload["phone"]
    assert "created_at" in data
    assert "is_processed" in data
    assert data["is_processed"] is False
