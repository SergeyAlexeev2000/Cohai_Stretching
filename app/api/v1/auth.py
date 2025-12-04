# app/api/v1/auth.py
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import (
    get_current_user,
    require_admin,
    require_superadmin,
)
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    decode_access_token,
)
from app.models.user import User, UserRole
from app.models.trainer import Trainer

from app.schemas.user_auth import (
    LoginIn,
    RegisterIn,
    TokenOut,
    UserOut,
    AdminCreateTrainer,       # НОВОЕ
    SuperadminCreateAdmin,    # НОВОЕ
)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def _ensure_email_unique(db: Session, email: str) -> None:
    stmt = select(User).where(User.email == email)
    existing = db.scalar(stmt)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Базовая зависимость получения текущего пользователя по JWT.

    TODO: при необходимости перенести в отдельный модуль (deps_auth.py),
    чтобы переиспользовать в админских ручках.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: Any = decode_access_token(token)
    except Exception:
        raise credentials_exception

    user_id: str | None = payload.get("sub") if isinstance(payload, dict) else None
    if user_id is None:
        raise credentials_exception

    stmt = select(User).where(User.id == int(user_id))
    user = db.scalar(stmt)

    if not user or not user.is_active:
        raise credentials_exception

    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterIn,
    db: Session = Depends(get_db),
) -> User:
    """
    Публичная регистрация нового клиента.

    По умолчанию всем даём роль CLIENT.
    """
    stmt = select(User).where(User.email == payload.email)
    existing = db.scalar(stmt)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        role=UserRole.CLIENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # ВАЖНО: возвращаем ORM-объект, FastAPI + Pydantic v2 сами применят from_attributes
    return user


@router.post("/login", response_model=TokenOut)
def login(
    payload: LoginIn,
    db: Session = Depends(get_db),
) -> TokenOut:
    """
    Логин по email + паролю, выдаём access_token.
    """
    stmt = select(User).where(User.email == payload.email)
    user = db.scalar(stmt)

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(
        subject=user.id,
        extra_claims={"role": user.role.value},
    )

    return TokenOut(access_token=access_token)


@router.get("/me", response_model=UserOut)
def read_me(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Вернуть данные текущего авторизованного пользователя.
    """
    return current_user


@router.post("/register-trainer", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_trainer(
    payload: AdminCreateTrainer,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> User:
    """
    Создание ТРЕНЕРА.

    Доступно для ADMIN и SUPERADMIN.
    - создаём User с ролью TRAINER
    - создаём Trainer и привязываем к этому User
    """
    _ensure_email_unique(db, payload.email)

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        role=UserRole.TRAINER,
        is_active=True,
    )
    db.add(user)
    db.flush()  # получаем user.id

    trainer = Trainer(
        full_name=payload.full_name or payload.email,
        user_id=user.id,
        # при желании можно добавить ещё поля (био, опыт и т.п.)
    )
    db.add(trainer)
    db.commit()
    db.refresh(user)

    return user

