from typing import List
from sqlalchemy.orm import Session

from app.models.membership import MembershipPlan


class MembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_location(self, location_id: int) -> List[MembershipPlan]:
        return (
            self.db.query(MembershipPlan)
            .filter(MembershipPlan.location_id == location_id)
            .all()
        )
