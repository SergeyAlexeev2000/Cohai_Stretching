# app/repositories/location_repo.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError  # если используешь централизованные ошибки
from app.models.location import Location


class LocationRepository:
    """Низкоуровневая работа с локациями (locations)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # --- базовые операции ---

    def list_all(self) -> List[Location]:
        """Вернуть все локации в порядке id."""
        stmt = select(Location).order_by(Location.id)
        return list(self.db.scalars(stmt).all())

    def get(self, location_id: int) -> Optional[Location]:
        """Вернуть локацию по id или None."""
        return self.db.get(Location, location_id)

    def get_by_id(self, location_id: int) -> Optional[Location]:
        """Совместимость со старым кодом."""
        return self.get(location_id)

    def get_or_404(self, location_id: int) -> Location:
        """Вернуть локацию или кинуть 404."""
        obj = self.get(location_id)
        if obj is None:
            raise AppError(
                code="LOCATION_NOT_FOUND",
                message=f"Location with id={location_id} not found",
                http_status=404,
            )
        return obj


    # --- CRUD ---

    def create(self, obj: Location) -> Location:
        """Создать новую локацию (add + flush). Коммит в сервисе."""
        self.db.add(obj)
        self.db.flush()
        return obj

    def save(self, obj: Location) -> Location:
        """Обновить существующую локацию (symmetry). Коммит в сервисе."""
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, obj: Location) -> None:
        """Удалить локацию в рамках текущей транзакции."""
        self.db.delete(obj)
