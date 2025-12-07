# app/api/v1/admin_memberships.py

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.schemas.membership import (
    MembershipPlanRead,
    MembershipPlanCreate,
    MembershipPlanUpdate,
)
from app.services.membership_service import MembershipService

# этот router будет подключен в app.main
router = APIRouter(
    prefix="/admin/memberships",
    tags=["admin_memberships"],
)


@router.get("/", response_model=list[MembershipPlanRead])
def list_memberships(
    location_id: Optional[int] = Query(
        default=None,
        description="Фильтр по локации",
    ),
    db: Session = Depends(get_db),
):
    """
    Список абонементов для админки.

    Пока только фильтрация по location_id.
    """
    service = MembershipService(db)
    return service.list_all(location_id=location_id)


@router.get("/{membership_id}", response_model=MembershipPlanRead)
def get_membership(
    membership_id: int,
    db: Session = Depends(get_db),
):
    """
    Получить один тариф по id.

    404, если не найден (через AppError + global_exception_handler).
    """
    service = MembershipService(db)
    return service.get_or_404(membership_id)


@router.post(
    "/",
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


@router.patch(
    "/{membership_id}",
    response_model=MembershipPlanRead,
)
def update_membership(
    membership_id: int,
    payload: MembershipPlanUpdate,
    db: Session = Depends(get_db),
):
    """
    Частично обновить тариф.
    """
    service = MembershipService(db)
    return service.update(membership_id, payload)


@router.delete(
    "/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_membership(
    membership_id: int,
    db: Session = Depends(get_db),
):
    """
    Удалить тариф.

    Возвращает 204 No Content при успехе.
    """
    service = MembershipService(db)
    service.delete(membership_id)
    # тело ответа пустое
