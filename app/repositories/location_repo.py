from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.location import Location


class LocationRepository:

    """Репозиторий для работы с локациями."""

    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> List[Location]:
        return self.db.query(Location).all()
    
    def get_by_id(self, location_id: int) -> Optional[Location]:
        return (
            self.db.query(Location)
            .filter(Location.id == location_id)
            .first()
        )
