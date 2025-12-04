# app/schemas/user_auth.py
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from pydantic import ConfigDict

from app.models.user import UserRole


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None
    phone: Optional[str] = None

# --- НОВОЕ: создание тренера админом/суперадмином ---

class AdminCreateTrainer(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    # здесь позже можно добавить поля для тренерского профиля:
    # bio: Optional[str] = None
    # experience_years: Optional[int] = None


# --- НОВОЕ: создание админа суперадмином ---

class SuperadminCreateAdmin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None
    phone: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    # Pydantic v2: говорим, что модель может читать атрибуты ORM-объекта
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole  # enum нормально поддерживается


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileOut(BaseModel):
    """Публичное представление профиля текущего пользователя."""

    id: int
    email: EmailStr
    role: UserRole
    full_name: str | None = None
    phone: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdateIn(BaseModel):
    """
    Данные для обновления профиля.

    - full_name / phone можно менять независимо.
    - Для смены пароля нужно указать и current_password, и new_password.
    """

    full_name: str | None = None
    phone: str | None = None

    current_password: str | None = Field(
        default=None,
        description="Текущий пароль (нужен, если меняем пароль).",
    )
    new_password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
        description="Новый пароль (минимум 8 символов).",
    )