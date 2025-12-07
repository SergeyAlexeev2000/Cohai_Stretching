# app/api/v1/me/memberships.py
from datetime import date

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import get_current_user
from app.models.membership import Membership, MembershipStatus
from app.models.user import User
from app.schemas.membership import MembershipRead, MembershipListResponse

from . import router


@router.get("/memberships", response_model=MembershipListResponse)
def my_memberships(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MembershipListResponse:
    """
    Вернуть абонементы текущего пользователя, разделённые на active/history.
    """
    stmt = (
        select(Membership)
        .where(Membership.user_id == current_user.id)
        .order_by(Membership.start_date.desc())
    )
    memberships = list(db.scalars(stmt).all())

    today = date.today()
    active: list[MembershipRead] = []
    history: list[MembershipRead] = []

    for m in memberships:
        is_active_status = m.status == MembershipStatus.ACTIVE.value
        is_not_expired = m.end_date >= today
        target = active if (is_active_status and is_not_expired) else history

        target.append(MembershipRead.model_validate(m))

    return MembershipListResponse(active=active, history=history)
