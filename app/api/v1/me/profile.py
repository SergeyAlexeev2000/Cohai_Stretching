# app/api/v1/me/profile.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import get_current_user
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user_auth import ProfileOut, ProfileUpdateIn

from . import router


@router.get("/profile", response_model=ProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    """Вернуть профиль текущего пользователя."""
    return current_user


@router.patch("/profile", response_model=ProfileOut)
def update_profile(
    payload: ProfileUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Обновить профиль текущего пользователя.
    """
    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    if payload.phone is not None:
        current_user.phone = payload.phone

    if payload.new_password is not None:
        if not payload.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to set a new password.",
            )

        if not verify_password(payload.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        current_user.password_hash = get_password_hash(payload.new_password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user
