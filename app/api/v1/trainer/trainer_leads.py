# app/api/v1/trainer/trainer_leads.py

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import require_role, get_current_user
from app.models.user import User, UserRole

from app.models.lead import LeadStatus
from app.schemas.lead import LeadRead, LeadUpdateTrainer
from app.services.lead_service import LeadService


# ---------------------------------------------------------------------------
#   ROUTER — доступ TRAINER, ADMIN, SUPERADMIN
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/trainer/leads",
    tags=["trainer_leads"],
    dependencies=[Depends(require_role(
        UserRole.TRAINER,
        UserRole.ADMIN,
        UserRole.SUPERADMIN,
    ))],
)


# ---------------------------------------------------------------------------
#   GET /trainer/leads — список лидов тренера
# ---------------------------------------------------------------------------

@router.get("", response_model=list[LeadRead])
def list_trainer_leads(
    status: Optional[LeadStatus] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Тренер может видеть только свои лиды.
    Админ и супер-админ — любые.
    """
    service = LeadService(db)
    return service.list_leads_for_trainer(
        trainer_id=current_user.id if current_user.role == UserRole.TRAINER else None,
        status=status,
    )


# ---------------------------------------------------------------------------
#   GET /trainer/leads/{lead_id}
# ---------------------------------------------------------------------------

@router.get("/{lead_id}", response_model=LeadRead)
def get_trainer_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Тренер видит только свои лиды.
    Админ — любой.
    """
    service = LeadService(db)
    return service.get_lead_for_trainer(lead_id, current_user)


# ---------------------------------------------------------------------------
#   PATCH /trainer/leads/{lead_id} — изменить лид тренером
# ---------------------------------------------------------------------------

@router.patch("/{lead_id}", response_model=LeadRead)
def update_trainer_lead(
    lead_id: int,
    payload: LeadUpdateTrainer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Тренер может обновлять только свои лиды.
    """
    service = LeadService(db)
    return service.update_lead_trainer(lead_id, payload, current_user)
