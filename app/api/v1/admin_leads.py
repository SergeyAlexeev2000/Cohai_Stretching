# app/api/v1/admin_leads.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.schemas.lead import LeadRead
from app.services.lead_service import LeadService

# это ТОТ САМЫЙ router, который ждёт app.main
router = APIRouter(
    prefix="/admin/leads",
    tags=["admin_leads"],
)


@router.get("/", response_model=list[LeadRead])
def list_leads(db: Session = Depends(get_db)):
    """
    Простой административный эндпоинт:
    вернуть список лидов.
    Главное - чтобы модуль имел router.
    """
    service = LeadService(db)
    # если в LeadService нет такого метода - можно временно вернуть пустой список
    return service.list_leads()  # или: return []
