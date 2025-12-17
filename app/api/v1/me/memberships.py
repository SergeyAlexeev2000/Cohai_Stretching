# app/api/v1/me/memberships.py
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import get_current_user
from app.models.user import User
from app.schemas.membership import MembershipListResponse
from app.services.user_membership_service import UserMembershipService

from . import router


@router.get("/memberships", response_model=MembershipListResponse)
def my_memberships(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MembershipListResponse:
    """
    Вернуть абонементы текущего пользователя, разделённые на active/history.
    """
    service = UserMembershipService(db)
    return service.list_for_user(current_user)
