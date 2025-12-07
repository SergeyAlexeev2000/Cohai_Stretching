# app/api/v1/me/leads.py
from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import get_current_user
from app.models.user import User
from app.schemas.lead import LeadRead
from app.services.lead_service import LeadService

from . import router


@router.get("/leads", response_model=List[LeadRead])
def my_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Вернуть все лиды, связанные с текущим пользователем.
    """
    service = LeadService(db)
    return service.list_for_user(current_user)
