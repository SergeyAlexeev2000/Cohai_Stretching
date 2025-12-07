# app/api/v1/public/locations.py
from sqlalchemy.orm import Session
from fastapi import Depends

from app.api.v1.deps import get_db
from app.repositories.location_repo import LocationRepository
from app.schemas.location import LocationRead

from . import router


@router.get("/locations", response_model=list[LocationRead])
def list_locations(db: Session = Depends(get_db)):
    repo = LocationRepository(db)
    return repo.list_all()
