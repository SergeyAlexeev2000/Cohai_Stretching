# tests/test_public_schedule.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_schedule_status_code():
    # после bootstrap первая локация должна иметь id=1
    resp = client.get("/public/schedule", params={"location_id": 1})
    assert resp.status_code == 200


def test_get_schedule_returns_list():
    resp = client.get("/public/schedule", params={"location_id": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # пока таблица class_sessions пустая, но это нормально
    # просто проверяем, что это список
