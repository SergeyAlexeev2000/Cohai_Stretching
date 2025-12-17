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


# -------------------------------------------------------------------------
#  AUTH — базовая проверка токена
# -------------------------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Достаёт текущего пользователя из JWT.
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

    user = db.scalar(select(User).where(User.id == user_id))
    if not user or not user.is_active:
        raise credentials_exception

    return user


# -------------------------------------------------------------------------
#  UNIVERSAL ROLE CHECK
# -------------------------------------------------------------------------

def require_role(*allowed_roles: UserRole | str):
    """
    Универсальная зависимость для проверки ролей.

    Пример:
        @router.get("/admin", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """
    allowed = {UserRole(r) if isinstance(r, str) else r for r in allowed_roles}
    if not allowed:
        raise RuntimeError("require_role() called without roles")

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return dependency


# -------------------------------------------------------------------------
#  BACKWARD-COMPATIBLE SHORTHAND HELPERS
# -------------------------------------------------------------------------

def require_superadmin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Только SUPERADMIN.
    """
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin privileges required",
        )
    return current_user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    ADMIN и SUPERADMIN.
    """
    if current_user.role not in (UserRole.ADMIN, UserRole.SUPERADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def require_trainer_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    TRAINER, ADMIN, SUPERADMIN.
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


# -------------------------------------------------------------------------
#  OPTIONAL USER — публичные эндпоинты, где токен не обязателен
# -------------------------------------------------------------------------

def get_current_user_optional(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Возвращает User или None:
    - нет Authorization → None
    - токен битый → None
    - токен просрочен → None
    - пользователь неактивен → None
    """
    if not authorization:
        return None

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

    user = db.scalar(select(User).where(User.id == user_id))
    if not user or not user.is_active:
        return None

    return user
