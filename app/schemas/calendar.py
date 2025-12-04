# app/schemas/calendar.py
from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel


class MeCalendarClassItem(BaseModel):
    """
    Одна конкретная запись пользователя на занятие для календаря.
    """

    attendance_id: int
    class_session_id: int

    class_date: date
    start_time: time
    end_time: time

    status: str


class MeCalendarDay(BaseModel):
    """
    День календаря: дата + список занятий в этот день.
    """

    date: date
    classes: list[MeCalendarClassItem]


class MeCalendarResponse(BaseModel):
    """
    Ответ для /api/v1/me/calendar:
    - start_date, end_date: границы диапазона
    - days: список дней, в которых у пользователя есть занятия
    """

    start_date: date
    end_date: date
    days: list[MeCalendarDay]
