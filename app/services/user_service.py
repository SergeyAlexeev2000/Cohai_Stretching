# app/services/user_service.py
from __future__ import annotations

from sqlalchemy.orm import Session

from fastapi import HTTPException, status  # либо AppError, если хочешь унифицировать
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user_auth import ProfileOut, ProfileUpdateIn


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_profile(self, current_user: User) -> ProfileOut:
        # тут можно просто обернуть в Pydantic-схему,
        # либо вернуть сам ORM-объект и пусть FastAPI его сериализует
        return ProfileOut.model_validate(current_user)

    def update_profile(self, current_user: User, payload: ProfileUpdateIn) -> User:
        # Обновляем базовые поля
        if payload.full_name is not None:
            current_user.full_name = payload.full_name
        if payload.phone is not None:
            current_user.phone = payload.phone

        # Смена пароля (если new_password задан)
        if payload.new_password:
            if not payload.current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required to change password.",
                )

            if not verify_password(payload.current_password, current_user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect.",
                )

            current_user.password_hash = get_password_hash(payload.new_password)

        self.db.add(current_user)
        self.db.commit()
        self.db.refresh(current_user)
        return current_user
