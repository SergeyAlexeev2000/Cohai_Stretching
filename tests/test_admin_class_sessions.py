# tests/test_admin_class_sessions.py

from datetime import time

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.db.session import SessionLocal
from app.models.trainer import Trainer

client = TestClient(app, raise_server_exceptions=False)


def _get_any_location_id() -> int:
    resp = client.get("/public/locations")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list) and len(data) >= 1
    return data[0]["id"]


def _get_any_program_type_id() -> int:
    resp = client.get("/public/program-types")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list) and len(data) >= 1
    return data[0]["id"]


def _get_any_trainer_id() -> int:
    """
    Берём любого тренера напрямую из БД.
    bootstrap_db гарантирует, что хотя бы один есть.
    """
    with SessionLocal() as db:
        trainer = db.scalars(select(Trainer)).first()
        assert trainer is not None
        return trainer.id


def _create_class_session_via_admin(
    weekday: int = 0,
    start: time = time(9, 0),
    end: time = time(10, 0),
):
    location_id = _get_any_location_id()
    program_type_id = _get_any_program_type_id()
    trainer_id = _get_any_trainer_id()

    payload = {
        "weekday": weekday,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "location_id": location_id,
        "program_type_id": program_type_id,
        "trainer_id": trainer_id,
        "membership_plan_id": None,
        "capacity": 10,
        "is_active": True,
    }

    resp = client.post("/api/v1/admin/class-sessions", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    return data


def test_admin_create_and_get_class_session():
    sess = _create_class_session_via_admin()

    resp = client.get(f"/api/v1/admin/class-sessions/{sess['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == sess["id"]
    assert data["weekday"] == 0
    assert data["capacity"] == 10
    assert "duration_minutes" in data


def test_admin_list_class_sessions_contains_created():
    sess = _create_class_session_via_admin(weekday=2)

    resp = client.get("/api/v1/admin/class-sessions")
    assert resp.status_code == 200
    data = resp.json()
    ids = [item["id"] for item in data]
    assert sess["id"] in ids


def test_admin_update_class_session_changes_time():
    sess = _create_class_session_via_admin(
        weekday=3,
        start=time(18, 0),
        end=time(19, 0),
    )

    resp_patch = client.patch(
        f"/api/v1/admin/class-sessions/{sess['id']}",
        json={"start_time": "19:00:00", "end_time": "20:00:00"},
    )
    assert resp_patch.status_code == 200
    data = resp_patch.json()
    assert data["start_time"].startswith("19:00")
    assert data["end_time"].startswith("20:00")

    # проверяем, что duration_minutes пересчитался
    assert data["duration_minutes"] == 60


def test_admin_delete_class_session_then_404_on_get():
    sess = _create_class_session_via_admin()

    resp_delete = client.delete(
        f"/api/v1/admin/class-sessions/{sess['id']}"
    )
    assert resp_delete.status_code == 204

    resp_get = client.get(
        f"/api/v1/admin/class-sessions/{sess['id']}"
    )
    assert resp_get.status_code == 404
