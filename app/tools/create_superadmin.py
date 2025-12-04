# app/tools/create_superadmin.py
from __future__ import annotations

import getpass

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def main() -> None:
    db = SessionLocal()
    try:
        email = input("Email суперадмина: ").strip()

        # Проверяем, нет ли уже такого пользователя
        stmt = select(User).where(User.email == email)
        existing = db.scalar(stmt)
        if existing:
            print(f"Пользователь с email {email!r} уже существует: id={existing.id}, role={existing.role}")
            return

        full_name = input("Имя (опционально): ").strip() or None
        phone = input("Телефон (опционально): ").strip() or None

        password = getpass.getpass("Пароль: ")
        password2 = getpass.getpass("Повторите пароль: ")
        if password != password2:
            print("Пароли не совпадают!")
            return

        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            password_hash=get_password_hash(password),
            role=UserRole.SUPERADMIN,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"Суперадмин создан: id={user.id}, email={user.email}, role={user.role}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
