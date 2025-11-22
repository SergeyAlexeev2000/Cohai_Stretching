# app/api/v1/public.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session


from app.api.v1.deps import get_db
from app.repositories.location_repo import LocationRepository
from app.repositories.program_type_repo import ProgramTypeRepository
from app.schemas.class_session import ClassSessionRead
from app.schemas.lead import LeadCreateGuestVisit, LeadRead
from app.schemas.location import LocationRead
from app.schemas.membership import MembershipPlanRead
from app.schemas.program_type import ProgramTypeRead
from app.services.lead_service import LeadService
from app.services.membership_service import MembershipService
from app.services.schedule_service import ScheduleService
from app.core.exceptions import AppError

router = APIRouter(tags=["public"])


@router.get("/locations", response_model=list[LocationRead])
def list_locations(db: Session = Depends(get_db)):
    repo = LocationRepository(db)
    return repo.list_all()


@router.get("/program-types", response_model=list[ProgramTypeRead])
def list_program_types(db: Session = Depends(get_db)):
    repo = ProgramTypeRepository(db)
    return repo.list_all()


@router.get("/schedule", response_model=list[ClassSessionRead])
def get_schedule(
    location_id: int = Query(...),
    db: Session = Depends(get_db),
):
    service = ScheduleService(db)
    return service.get_schedule_for_location(location_id)


@router.get("/memberships", response_model=list[MembershipPlanRead])
def get_memberships(
    location_id: Optional[int] = Query(
        default=None,
        description="Фильтрация по локации. Если не задано — вернуть тарифы по всем локациям.",
    ),
    db: Session = Depends(get_db),
):
    """
    Публичный список абонементов.

    - Если location_id не передан — возвращаем все активные тарифы по всем локациям.
    - Если location_id передан — валидируем существование локации, затем фильтруем.
    """
    # Валидация location_id, если он указан
    if location_id is not None:
        loc_repo = LocationRepository(db)
        location = loc_repo.get_by_id(location_id)
        if location is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with id={location_id} not found",
            )
    
    service = MembershipService(db)
    # only_active=True — для публичного API показываем только актуальные тарифы
    return service.list_all(location_id=location_id, only_active=True)

@router.get("/memberships/{membership_id}", response_model=MembershipPlanRead)
def get_membership(
    membership_id: int,
    db: Session = Depends(get_db),
):
    """
    Публичный эндпоинт: один абонемент по id.
    """
    service = MembershipService(db)
    plan = service.get(membership_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership with id={membership_id} not found",
        )
    return plan


@router.post("/leads/guest-visit", response_model=LeadRead)
def create_guest_visit(
    payload: LeadCreateGuestVisit,
    db: Session = Depends(get_db),
):
    service = LeadService(db)
    return service.create_guest_visit(payload)


