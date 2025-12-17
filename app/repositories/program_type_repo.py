# app/repositories/program_type_repo.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.program_type import ProgramType


class ProgramTypeRepository:
    """Низкоуровневая работа с типами программ (program_types)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # --- базовые операции ---

    def list_all(self) -> List[ProgramType]:
        """Вернуть все типы программ, отсортированные по id."""
        stmt = select(ProgramType).order_by(ProgramType.id)
        return list(self.db.scalars(stmt).all())

    def get(self, program_type_id: int) -> Optional[ProgramType]:
        """Получить тип программы по id или None."""
        return self.db.get(ProgramType, program_type_id)

    def get_or_404(self, program_type_id: int) -> ProgramType:
        """Получить тип программы или кинуть AppError(404)."""
        obj = self.get(program_type_id)
        if obj is None:
            raise AppError(
                code="PROGRAM_TYPE_NOT_FOUND",
                message=f"ProgramType with id={program_type_id} not found",
                http_status=404,
            )
        return obj

    # --- CRUD (на будущее/для админки) ---

    def create(self, obj: ProgramType) -> ProgramType:
        """
        Создать новый ProgramType (add + flush).
        Коммит должен быть на уровне сервиса.
        """
        self.db.add(obj)
        self.db.flush()
        return obj

    def save(self, obj: ProgramType) -> ProgramType:
        """
        Обновление ProgramType (если понадобится).
        """
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, obj: ProgramType) -> None:
        """Удалить ProgramType в рамках текущей транзакции."""
        self.db.delete(obj)
