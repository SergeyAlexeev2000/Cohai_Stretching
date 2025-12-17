# app/api/v1/admin/admin_leads.py

from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import require_role
from app.models.user import UserRole

from app.models.lead import LeadStatus
from app.schemas.lead import LeadRead, LeadUpdateAdmin
from app.services.lead_service import LeadService


# ---------------------------------------------------------------------------
#   ROUTER — доступ только ADMIN и SUPERADMIN
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/admin/leads",
    tags=["admin_leads"],
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.SUPERADMIN))],
)


# ---------------------------------------------------------------------------
#   GET /admin/leads/by-status — фильтр лидов администратора
# ---------------------------------------------------------------------------

@router.get("/by-status", response_model=list[LeadRead])
def admin_list_leads(
    status: LeadStatus | None = Query(default=None),
    trainer_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Список лидов с фильтрами:
    - по статусу
    - по тренеру
    """
    service = LeadService(db)
    leads = service.list_leads_for_admin(status=status, trainer_id=trainer_id)
    return leads


# ---------------------------------------------------------------------------
#   PATCH /admin/leads/{lead_id} — обновление от администратора
# ---------------------------------------------------------------------------

@router.patch("/{lead_id}", response_model=LeadRead)
def admin_update_lead(
    lead_id: int,
    payload: LeadUpdateAdmin,
    db: Session = Depends(get_db),
):
    service = LeadService(db)
    lead = service.update_lead_admin(lead_id, payload)
    return lead


# ---------------------------------------------------------------------------
#   DELETE /admin/leads/{lead_id} — удалить лид
# ---------------------------------------------------------------------------

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    service = LeadService(db)
    service.delete_lead(lead_id)
    return None


# ---------------------------------------------------------------------------
#   GET /admin/leads — общий список лидов
# ---------------------------------------------------------------------------

@router.get("", response_model=list[LeadRead])
def list_leads(
    is_processed: Optional[bool] = Query(
        default=None,
        description="Фильтр по обработанности лида",
    ),
    location_id: Optional[int] = Query(
        default=None,
        description="Фильтр по локации",
    ),
    program_type_id: Optional[int] = Query(
        default=None,
        description="Фильтр по типу программы",
    ),
    q: Optional[str] = Query(
        default=None,
        description="Поиск по имени или телефону (подстрока)",
    ),
    db: Session = Depends(get_db),
):
    """
    Главный админ-список лидов.
    """
    service = LeadService(db)
    return service.list_leads(
        is_processed=is_processed,
        location_id=location_id,
        program_type_id=program_type_id,
        query=q,
    )


# ---------------------------------------------------------------------------
#   GET /admin/leads/{lead_id} — получить лид
# ---------------------------------------------------------------------------

@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    """
    Получить лид по ID.
    """
    service = LeadService(db)
    return service.get_lead(lead_id)


# ---------------------------------------------------------------------------
#   PATCH /admin/leads/{lead_id}/process — отметить обработанным
# ---------------------------------------------------------------------------

@router.patch("/{lead_id}/process", response_model=LeadRead)
def process_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    """
    Помечает лид как обработанный.
    Идемпотентно.
    """
    service = LeadService(db)
    return service.mark_processed(lead_id)
