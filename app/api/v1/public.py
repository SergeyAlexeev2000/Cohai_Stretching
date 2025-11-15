print("LOADING public.py, __name__ =", __name__)

from fastapi import APIRouter, Depends, Query
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
    location_id: int = Query(...),
    db: Session = Depends(get_db),
):
    service = MembershipService(db)
    return service.list_for_location(location_id)


@router.post("/leads/guest-visit", response_model=LeadRead)
def create_guest_visit(
    payload: LeadCreateGuestVisit,
    db: Session = Depends(get_db),
):
    service = LeadService(db)
    return service.create_guest_visit(payload)
