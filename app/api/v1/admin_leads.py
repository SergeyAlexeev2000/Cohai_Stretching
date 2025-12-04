# app/api/v1/admin_leads.py

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import require_admin

from app.models.lead import LeadStatus

from app.schemas.lead import LeadRead, LeadUpdateAdmin

from app.services.lead_service import LeadService

# этот router уже подключён в app.main:
# app.include_router(admin_leads_router, prefix="/api/v1")
router = APIRouter(
    prefix="/admin/leads",
    tags=["admin_leads"],
    dependencies=[Depends(require_admin)],  # ← все ручки под этим роутером требуют ADMIN
)

@router.get("/by-status", response_model=list[LeadRead])
def admin_list_leads(
    status: LeadStatus | None = Query(default=None),
    trainer_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = LeadService(db)
    leads = service.list_leads_for_admin(status=status, trainer_id=trainer_id)
    return leads


@router.patch("/{lead_id}", response_model=LeadRead)
def admin_update_lead(
    lead_id: int,
    payload: LeadUpdateAdmin,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = LeadService(db)
    lead = service.update_lead_admin(lead_id, payload)
    return lead


@router.delete("/{lead_id}", status_code=204)
def admin_delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = LeadService(db)
    service.delete_lead(lead_id)
    return None


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
    Админский список лидов с фильтрами.

    Пример запросов:
    - GET /api/v1/admin/leads
    - GET /api/v1/admin/leads?is_processed=false
    - GET /api/v1/admin/leads?location_id=1
    - GET /api/v1/admin/leads?q=+373
    """
    service = LeadService(db)
    
    return service.list_leads(
        is_processed=is_processed,
        location_id=location_id,
        program_type_id=program_type_id,
        query=q,
    )


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    """
    Получить один лид по id.

    404 если не найден (через AppError → global_exception_handler).
    """
    service = LeadService(db)
    return service.get_lead(lead_id)


@router.patch("/{lead_id}/process", response_model=LeadRead)
def process_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    """
    Отметить лид как обработанный.

    Идемпотентно: повторный вызов просто вернёт уже обработанный лид.
    """
    service = LeadService(db)
    return service.mark_processed(lead_id)


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
):
    """
    Удалить лид.

    Возвращает 204 No Content при успехе.
    """
    service = LeadService(db)
    service.delete_lead(lead_id)
    # тело ответа пустое

