# app/core/security.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import os

from jose import jwt
from passlib.context import CryptContext

# TODO: при желании можно перенести это в app.core.config.Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_PLEASE")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

# ВАЖНО:
# используем НЕ bcrypt, а pbkdf2_sha256 — у него нет ограничения 72 байта.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def _normalize_password(password: str) -> str:
    """
    Безопасно нормализуем пароль:
    - кодируем в utf-8
    - обрезаем до 256 байт (на всякий случай)
    - декодируем обратно, игнорируя обрезанный хвост в середине символа
    """
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > 256:
        pw_bytes = pw_bytes[:256]
    return pw_bytes.decode("utf-8", errors="ignore")


def get_password_hash(password: str) -> str:
    """Захэшировать пароль для сохранения в БД."""
    normalized = _normalize_password(password)
    return pwd_context.hash(normalized)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля при логине."""
    normalized = _normalize_password(plain_password)
    return pwd_context.verify(normalized, hashed_password)


def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    subject — обычно user.id, который кладём в claim "sub".
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    to_encode: Dict[str, Any] = {"sub": str(subject), "iat": now, "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Обёртка вокруг jwt.decode.
    Бросает JWTError/ExpiredSignatureError при проблемах.
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return payload
