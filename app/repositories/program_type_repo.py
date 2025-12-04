# app/repositories/program_type_repo.py

from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.program_type import ProgramType


class ProgramTypeRepository:
    """Работа с типами программ (program_types)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> List[ProgramType]:
        """Вернуть все типы программ."""
        stmt = select(ProgramType).order_by(ProgramType.id)
        return list(self.db.scalars(stmt).all())
