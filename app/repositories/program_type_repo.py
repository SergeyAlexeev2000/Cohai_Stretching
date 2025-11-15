# app/repositories/program_type_repo.py
from typing import List

from sqlalchemy.orm import Session

from app.models.program_type import ProgramType


class ProgramTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> List[ProgramType]:
        return self.db.query(ProgramType).all()
