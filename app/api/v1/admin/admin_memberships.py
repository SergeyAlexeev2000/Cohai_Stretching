# app/api/v1/admin/admin_memberships.py

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import require_role
from app.models.user import UserRole

from app.schemas.membership import (
    MembershipPlanRead,
    MembershipPlanCreate,
    MembershipPlanUpdate,
)
from app.services.membership_service import MembershipService


router = APIRouter(
    prefix="/admin/memberships",
    tags=["admin_memberships"],
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.SUPERADMIN))],
)


@router.get("", response_model=list[MembershipPlanRead])
def list_memberships(
    db: Session = Depends(get_db),
):
    """
    Получить список всех тарифов (абонементных планов).
    """
    service = MembershipService(db)
    return service.list_all()


@router.get("/{membership_id}", response_model=MembershipPlanRead)
def get_membership(
    membership_id: int,
    db: Session = Depends(get_db),
):
    """
    Получить тариф по ID.
    """
    service = MembershipService(db)
    return service.get_or_404(membership_id)


@router.post(
    "",
    response_model=MembershipPlanRead,
    status_code=status.HTTP_201_CREATED,
)
def create_membership(
    payload: MembershipPlanCreate,
    db: Session = Depends(get_db),
):
    """
    Создать новый тариф.
    """
    service = MembershipService(db)
    return service.create(payload)


@router.patch("/{membership_id}", response_model=MembershipPlanRead)
def update_membership(
    membership_id: int,
    payload: MembershipPlanUpdate,
    db: Session = Depends(get_db),
):
    """
    Обновить существующий тариф.
    """
    service = MembershipService(db)
    return service.update(membership_id, payload)


@router.delete("/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership(
    membership_id: int,
    db: Session = Depends(get_db),
):
    """
    Удалить тариф.
    """
    service = MembershipService(db)
    service.delete(membership_id)
    return None
