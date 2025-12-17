# app/api/v1/me/profile.py
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import get_current_user
from app.models.user import User
from app.schemas.user_auth import ProfileOut, ProfileUpdateIn
from app.services.user_service import UserService

from . import router


@router.get("/profile", response_model=ProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileOut:
    """Вернуть профиль текущего пользователя."""
    service = UserService(db)
    return service.get_profile(current_user)


@router.patch("/profile", response_model=ProfileOut)
def update_profile(
    payload: ProfileUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileOut:
    """
    Обновить профиль текущего пользователя.
    """
    service = UserService(db)
    updated_user = service.update_profile(current_user, payload)
    # если UserService уже возвращает ProfileOut, можно просто вернуть его;
    # если возвращает ORM User — оборачиваем:
    return ProfileOut.model_validate(updated_user)
