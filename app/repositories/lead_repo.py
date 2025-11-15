from typing import List
from sqlalchemy.orm import Session

from app.models.lead import Lead


class LeadRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_guest_visit(self, data: dict) -> Lead:
        lead = Lead(**data)
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def list_all(self) -> List[Lead]:
        return self.db.query(Lead).all()

    def mark_processed(self, lead_id: int) -> None:
        lead = self.db.query(Lead).get(lead_id)
        if lead:
            lead.is_processed = True
            self.db.commit()
