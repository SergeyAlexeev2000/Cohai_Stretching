from typing import List
from sqlalchemy.orm import Session

from app.models.class_session import ClassSession


class ClassSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_location(self, location_id: int) -> List[ClassSession]:
        return (
            self.db.query(ClassSession)
            .filter(ClassSession.location_id == location_id)
            .all()
        )
