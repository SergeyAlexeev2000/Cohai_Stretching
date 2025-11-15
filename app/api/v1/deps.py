# app/api/v1/deps.py
from typing import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость FastAPI, которая отдаёт сессию БД и корректно её закрывает.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
