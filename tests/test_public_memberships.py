# tests/test_public_memberships.py

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_memberships_status_code():
    """Проверяем, что эндпоинт /api/v1/memberships отвечает 200."""
    response = client.get("/api/v1/memberships")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_memberships_with_invalid_location_returns_404():
    """Если передать несуществующий location_id, должен быть 404."""
    # Предполагаем, что location_id=99999 не существует.
    response = client.get("/api/v1/memberships?location_id=99999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_get_membership_not_found():
    """Запрос к несуществующему membership_id должен вернуть 404."""
    response = client.get("/api/v1/memberships/99999")
    assert response.status_code == 404


# Этот тест можно включить, если ты знаешь гарантированно существующий ID
# (например, bootstrap_db создаёт membership с id=1)
#
# def test_get_membership_ok():
#     response = client.get("/api/v1/memberships/1")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["id"] == 1
#     assert "name" in data
