# app/schemas/location.py

from typing import Optional

from pydantic import BaseModel


class LocationBase(BaseModel):
    """Базовая схема локации (общие поля)."""
    name: str
    address: Optional[str] = None

    class Config:
        orm_mode = True


class LocationRead(LocationBase):
    """То, что мы отдаем наружу (в API)."""
    id: int


class LocationCreate(LocationBase):
    """Если потом понадобится создавать локации через API."""
    pass


class LocationUpdate(BaseModel):
    """Схема для обновления (вдруг пригодится)."""
    name: Optional[str] = None
    address: Optional[str] = None

    class Config:
        orm_mode = True


__all__ = [
    "LocationBase",
    "LocationRead",
    "LocationCreate",
    "LocationUpdate",
]
