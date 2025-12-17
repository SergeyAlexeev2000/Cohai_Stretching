# app/services/user_membership_service.py

from __future__ import annotations

from datetime import date
from typing import List

from sqlalchemy.orm import Session

from app.models.membership import Membership, MembershipStatus
from app.models.user import User
from app.repositories.user_membership_repo import UserMembershipRepository
from app.schemas.membership import MembershipRead, MembershipListResponse


class UserMembershipService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserMembershipRepository(db)

    def list_for_user(self, user: User) -> MembershipListResponse:
        # низкоуровневый доступ к БД — через репозиторий
        memberships: List[Membership] = self.repo.list_for_user(user.id)

        today = date.today()
        active: list[MembershipRead] = []
        history: list[MembershipRead] = []

        for m in memberships:
            is_active_status = m.status == MembershipStatus.ACTIVE.value
            is_not_expired = m.end_date >= today
            target = active if (is_active_status and is_not_expired) else history

            # используем Pydantic v2 model_validate для ORM
            target.append(MembershipRead.model_validate(m))

        return MembershipListResponse(active=active, history=history)
