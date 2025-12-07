# app/api/v1/public/memberships.py
from typing import Optional

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.repositories.location_repo import LocationRepository
from app.schemas.membership import MembershipPlanRead
from app.services.membership_service import MembershipService

from . import router


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
    if location_id is not None:
        loc_repo = LocationRepository(db)
        location = loc_repo.get_by_id(location_id)
        if location is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with id={location_id} not found",
            )

    service = MembershipService(db)
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
