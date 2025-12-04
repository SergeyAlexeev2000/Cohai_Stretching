# app/schemas/attendance.py
from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel


class MeClassItem(BaseModel):
    """
    Один класс в ЛК пользователя: запись на конкретное занятие.
    """

    attendance_id: int
    class_session_id: int

    class_date: date
    start_time: time
    end_time: time

    status: str


class MeClassesResponse(BaseModel):
    """
    Ответ для /api/v1/me/classes:
    - upcoming: будущие занятия, на которые пользователь записан
    - history: прошедшие / посещённые / пропущенные / отменённые
    """

    upcoming: list[MeClassItem]
    history: list[MeClassItem]


class ClassBookingRequest(BaseModel):
    """
    Тело для POST /api/v1/me/classes/book.
    """
    class_session_id: int
    class_date: date


class ClassCancelRequest(BaseModel):
    """
    Тело для POST /api/v1/me/classes/cancel.
    """
    attendance_id: int