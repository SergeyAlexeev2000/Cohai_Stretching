# app/api/v1/deps_auth.py
from __future__ import annotations

from typing import Any, Optional

from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Достаём текущего пользователя из JWT.
    Если токен битый / просрочен / пользователь неактивен — 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: Any = decode_access_token(token)
    except Exception:
        # JWTError, ExpiredSignatureError и т.п.
        raise credentials_exception

    if not isinstance(payload, dict):
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise credentials_exception

    stmt = select(User).where(User.id == user_id)
    user = db.scalar(stmt)

    if not user or not user.is_active:
        raise credentials_exception

    return user

def require_superadmin(current_user: User = Depends(get_current_user)) -> User:
    """
    Доступ только для SUPERADMIN.
    """
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin privileges required",
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Доступ для ADMIN и SUPERADMIN.
    """
    if current_user.role not in (UserRole.ADMIN, UserRole.SUPERADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def require_trainer_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Для тренерских эндпоинтов: TRAINER, ADMIN, SUPERADMIN.
    """
    if current_user.role not in (
        UserRole.TRAINER,
        UserRole.ADMIN,
        UserRole.SUPERADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Trainer or admin privileges required",
        )
    return current_user


def get_current_user_optional(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Опциональный текущий пользователь:
    - если нет заголовка Authorization → возвращаем None;
    - если токен битый/просрочен → тоже возвращаем None, без 401.
    """
    if not authorization:
        return None

    # ожидаем формат "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]

    try:
        payload: Any = decode_access_token(token)
    except Exception:
        return None

    if not isinstance(payload, dict):
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    stmt = select(User).where(User.id == user_id)
    user = db.scalar(stmt)

    if not user or not user.is_active:
        return None