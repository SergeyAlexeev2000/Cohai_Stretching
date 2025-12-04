# app/services/location_service.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate
from app.core.exceptions import AppError


class LocationService:
    """Бизнес-логика для локаций (студий)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # --- Публичный/общий список ---

    def list_all(self) -> List[Location]:
        """Вернуть все локации (пока без фильтров)."""
        stmt = select(Location).order_by(Location.id)
        return list(self.db.scalars(stmt).all())

    def get(self, location_id: int) -> Optional[Location]:
        """Вернуть локацию по id или None."""
        stmt = select(Location).where(Location.id == location_id)
        return self.db.scalars(stmt).first()

    # --- Вспомогательное для админки ---

    def get_or_404(self, location_id: int) -> Location:
        """Вернуть локацию или кинуть 404 через AppError."""
        location = self.get(location_id)
        if location is None:
            raise AppError(
                code="LOCATION_NOT_FOUND",
                message=f"Location with id={location_id} not found",
                http_status=404,
                extra={"location_id": location_id},
            )
        return location

    # --- CRUD для админки ---

    def create(self, payload: LocationCreate) -> Location:
        """Создать новую локацию."""
        location = Location(
            name=payload.name,
            address=payload.address,
            # если потом появятся поля city/lat/lng/is_active — добавим их тут
        )
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location

    def update(self, location_id: int, payload: LocationUpdate) -> Location:
        """
        Частично обновить локацию.
        Все поля в LocationUpdate опциональны → обновляем только переданные.
        """
        location = self.get_or_404(location_id)

        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(location, field, value)

        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location

    def delete(self, location_id: int) -> None:
        """Удалить локацию."""
        location = self.get_or_404(location_id)
        self.db.delete(location)
        self.db.commit()
