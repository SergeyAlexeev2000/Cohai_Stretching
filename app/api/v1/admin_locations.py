# app/api/v1/admin_locations.py

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.schemas.location import (
    LocationRead,
    LocationCreate,
    LocationUpdate,
)
from app.services.location_service import LocationService

router = APIRouter(
    prefix="/admin/locations",
    tags=["admin_locations"],
)


@router.get("/", response_model=list[LocationRead])
def list_locations(
    db: Session = Depends(get_db),
):
    """
    Список всех локаций.
    """
    service = LocationService(db)
    return service.list_all()


@router.get("/{location_id}", response_model=LocationRead)
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
):
    """
    Получить одну локацию по id.
    """
    service = LocationService(db)
    return service.get_or_404(location_id)


@router.post(
    "/",
    response_model=LocationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
):
    """
    Создать новую локацию.
    """
    service = LocationService(db)
    return service.create(payload)


@router.patch(
    "/{location_id}",
    response_model=LocationRead,
)
def update_location(
    location_id: int,
    payload: LocationUpdate,
    db: Session = Depends(get_db),
):
    """
    Частично обновить локацию.
    """
    service = LocationService(db)
    return service.update(location_id, payload)


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
):
    """
    Удалить локацию.
    """
    service = LocationService(db)
    service.delete(location_id)
    # 204 — тело ответа пустое
