# app/api/v1/trainer_leads.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import require_trainer_or_admin
from app.models.user import User, UserRole
from app.models.lead import LeadStatus
from app.schemas.lead import LeadRead, LeadUpdateAdmin
from app.services.lead_service import LeadService

router = APIRouter(
    prefix="/trainer/leads",
    tags=["trainer: leads"],
)


@router.get("", response_model=list[LeadRead])
def list_trainer_leads(
    status: LeadStatus | None = Query(default=None),
    trainer_id: int | None = Query(
        default=None,
        description="Для админа: явно указать тренера; для тренера игнорируется",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    """
    Для TRAINER:
      - возвращаем лиды, привязанные к его тренерскому профилю.

    Для ADMIN/SUPERADMIN:
      - если trainer_id указан -> лиды этого тренера;
      - если trainer_id не указан -> все лиды (как /admin/leads).
    """
    service = LeadService(db)

    # TRAINER
    if current_user.role == UserRole.TRAINER:
        if current_user.trainer_profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trainer profile is not linked to the user",
            )
        return service.list_leads_for_trainer(
            trainer_id=current_user.trainer_profile.id,
            status=status,
        )

    # ADMIN / SUPERADMIN
    if current_user.role in (UserRole.ADMIN, UserRole.SUPERADMIN):
        # Если trainer_id указан — фильтруем по нему;
        # если нет — вернём все лиды (чтобы было удобно в UI).
        return service.list_leads_for_admin(
            status=status,
            trainer_id=trainer_id,
        )

    # Теоретически сюда не попадём, но на всякий
    raise HTTPException(status_code=403, detail="Not allowed")


@router.patch("/{lead_id}", response_model=LeadRead)
def trainer_update_lead(
    lead_id: int,
    payload: LeadUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    """
    TRAINER:
      - может обновлять только свои лиды (assigned_trainer_id == его trainer.id)
      - в основном статус (IN_PROGRESS, CLOSED, и т.п.)

    ADMIN/SUPERADMIN:
      - может обновлять любые лиды.
    """
    service = LeadService(db)

    # ADMIN / SUPERADMIN – просто обновляем
    if current_user.role in (UserRole.ADMIN, UserRole.SUPERADMIN):
        return service.update_lead_admin(lead_id, payload)

    # TRAINER – сначала проверяем, его ли это лид
    if current_user.trainer_profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trainer profile is not linked to the user",
        )

    lead = service._get_or_404(lead_id)
    if lead.assigned_trainer_id != current_user.trainer_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify leads of other trainers",
        )

    # Ограничить поля, которые тренер может менять (если хочешь)
    safe_payload = LeadUpdateAdmin(
        status=payload.status,
        assigned_trainer_id=None,
        assigned_admin_id=None,
    )
    return service.update_lead_admin(lead_id, safe_payload)
