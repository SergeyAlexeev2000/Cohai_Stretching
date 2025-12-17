# app/services/auth_service.py
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.models.user import User, UserRole
from app.models.trainer import Trainer
from app.schemas.user_auth import (
    LoginIn,
    TokenOut,
    RegisterIn,
    AdminCreateTrainer,
    SuperadminCreateAdmin,
    UserOut,
)

from app.repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    # --- login ---

    def login(self, payload: LoginIn) -> TokenOut:
        user = self.users.get_by_email(payload.email)

        if not user or not verify_password(payload.password, user.password_hash):
            # ошибка аутентификации, как было в старом auth.py
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        access_token = create_access_token(
            subject=user.id,
            extra_claims={"role": user.role.value},
        )
        return TokenOut(access_token=access_token)
    
    # --- внутренний хелпер ---

    def _ensure_email_unique(self, email: str) -> None:
        """Проверяем, что пользователя с таким email ещё нет."""
        existing = self.users.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

    # --- register client ---

    def register_client(self, payload: RegisterIn) -> User:
        self._ensure_email_unique(payload.email)

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            phone=payload.phone,
            password_hash=get_password_hash(payload.password),
            role=UserRole.CLIENT,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # --- register trainer (ADMIN / SUPERADMIN) ---

    def register_trainer(self, payload: AdminCreateTrainer) -> User:
        self._ensure_email_unique(payload.email)

        user = User(
            email=payload.email,
            full_name=payload.full_name or payload.email,
            phone=payload.phone,
            password_hash=get_password_hash(payload.password),
            role=UserRole.TRAINER,
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()  # чтобы появился user.id

        trainer = Trainer(
            full_name=payload.full_name or payload.email,
            user_id=user.id,
        )
        self.db.add(trainer)

        self.db.commit()
        self.db.refresh(user)
        return user

    # --- create admin (SUPERADMIN only) ---

    def superadmin_create_admin(self, payload: SuperadminCreateAdmin) -> User:
        self._ensure_email_unique(payload.email)

        user = User(
            email=payload.email,
            full_name=payload.full_name or payload.email,
            phone=payload.phone,
            password_hash=get_password_hash(payload.password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
