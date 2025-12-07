# app/api/v1/public/program_types.py
from sqlalchemy.orm import Session
from fastapi import Depends

from app.api.v1.deps import get_db
from app.repositories.program_type_repo import ProgramTypeRepository
from app.schemas.program_type import ProgramTypeRead

from . import router


@router.get("/program-types", response_model=list[ProgramTypeRead])
def list_program_types(db: Session = Depends(get_db)):
    repo = ProgramTypeRepository(db)
    return repo.list_all()
