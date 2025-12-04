# app/repositories/location_repo.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.location import Location


class LocationRepository:
    """Работа с локациями (locations)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> List[Location]:
        """Вернуть все локации."""
        stmt = select(Location).order_by(Location.id)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, location_id: int) -> Optional[Location]:
        """Найти локацию по id или вернуть None."""
        stmt = select(Location).where(Location.id == location_id)
        return self.db.scalars(stmt).first()
