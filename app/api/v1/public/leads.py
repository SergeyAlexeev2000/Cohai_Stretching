# app/api/v1/public/leads.py
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import get_current_user_optional
from app.models.user import User
from app.schemas.lead import LeadCreateGuestVisit, LeadRead
from app.services.lead_service import LeadService

from . import router


@router.post("/leads/guest-visit", response_model=LeadRead)
def create_guest_visit(
    payload: LeadCreateGuestVisit,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Публичное создание лида.

    Если запрос приходит с токеном (авторизованный пользователь),
    привязываем лид к этому пользователю (lead.user_id = current_user.id).
    Если без токена — создаём лид без user_id (анонимный).
    """
    service = LeadService(db)
    lead = service.create_guest_visit(payload=payload, user=current_user)
    return lead
