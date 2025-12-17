# app/repositories/user_repo.py

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.user import User


class UserRepository:
    """Низкоуровневая работа с пользователями."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # --- базовые операции ---

    def get(self, user_id: int) -> Optional[User]:
        """Вернуть пользователя по id или None."""
        return self.db.get(User, user_id)

    def get_or_404(self, user_id: int) -> User:
        """Вернуть пользователя или кинуть 404."""
        obj = self.get(user_id)
        if obj is None:
            raise AppError(
                code="USER_NOT_FOUND",
                message=f"User with id={user_id} not found",
                http_status=404,
            )
        return obj

    def get_by_email(self, email: str) -> Optional[User]:
        """Вернуть пользователя по email или None."""
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def ensure_email_unique(self, email: str) -> None:
        """Кинуть ошибку, если пользователь с таким email уже существует."""
        if self.get_by_email(email) is not None:
            raise AppError(
                code="USER_EMAIL_NOT_UNIQUE",
                message="User with this email already exists",
                http_status=400,
            )

    # --- CRUD ---

    def create(self, user: User) -> User:
        """
        Создать нового пользователя (add + flush).
        Коммит — только на уровне сервиса!
        """
        self.db.add(user)
        self.db.flush()
        return user

    def save(self, user: User) -> User:
        """
        Обновить существующего пользователя.
        Коммит — только в сервисе.
        """
        self.db.add(user)
        self.db.flush()
        return user

    def delete(self, user: User) -> None:
        """Удалить пользователя в рамках текущей транзакции."""
        self.db.delete(user)
