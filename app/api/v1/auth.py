# app/api/v1/auth.py
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import (
    get_current_user,
    require_admin,
    require_superadmin,
)
from app.models.user import User
from app.schemas.user_auth import (
    LoginIn,
    RegisterIn,
    TokenOut,
    UserOut,
    AdminCreateTrainer,
    SuperadminCreateAdmin,
)
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterIn,
    db: Session = Depends(get_db),
) -> User:
    """
    Публичная регистрация нового клиента.

    По умолчанию всем даём роль CLIENT.
    """
    service = AuthService(db)
    user = service.register_client(payload)
    return user


@router.post("/login", response_model=TokenOut)
def login(
    payload: LoginIn,
    db: Session = Depends(get_db),
) -> TokenOut:
    """
    Логин по email + паролю, выдаём access_token.
    """
    service = AuthService(db)
    return service.login(payload)


@router.get("/me", response_model=UserOut)
def read_me(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Вернуть данные текущего авторизованного пользователя.
    """
    return current_user


@router.post(
    "/register-trainer",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register_trainer(
    payload: AdminCreateTrainer,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    """
    Создание ТРЕНЕРА.

    Доступно для ADMIN и SUPERADMIN.
    - создаём User с ролью TRAINER
    - создаём Trainer и привязываем к этому User
    """
    service = AuthService(db)
    user = service.register_trainer(payload)
    return user


@router.post(
    "/superadmin/create-admin",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def superadmin_create_admin(
    payload: SuperadminCreateAdmin,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
) -> User:
    """
    Создание ADMIN пользователем с ролью SUPERADMIN.

    SUPERADMIN может выдавать права ADMIN другим пользователям.
    """
    service = AuthService(db)
    user = service.superadmin_create_admin(payload)
    return user
