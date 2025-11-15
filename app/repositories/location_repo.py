from typing import List
from sqlalchemy.orm import Session

from app.models.location import Location


class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> List[Location]:
        return self.db.query(Location).all()
