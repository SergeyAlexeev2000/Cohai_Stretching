# app/services/attendance_service.py

from __future__ import annotations

from datetime import date
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceStatus
from app.models.class_session import ClassSession
from app.models.user import User
from app.schemas.attendance import (
    MeClassItem,
    MeClassesResponse,
    ClassBookingRequest,
    ClassCancelRequest,
)
from app.schemas.calendar import MeCalendarClassItem, MeCalendarDay, MeCalendarResponse


class AttendanceService:
    """Бизнес-логика для записей на занятия (attendances) в личном кабинете."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ---------- Мои занятия (список) ----------

    def get_my_classes(self, user: User) -> MeClassesResponse:
        today = date.today()

        stmt = (
            select(Attendance, ClassSession)
            .join(ClassSession, Attendance.class_session_id == ClassSession.id)
            .where(Attendance.user_id == user.id)
            .order_by(Attendance.class_date, ClassSession.start_time)
        )

        rows = self.db.execute(stmt).all()

        upcoming: list[MeClassItem] = []
        history: list[MeClassItem] = []

        for attendance, session in rows:
            is_future_or_today = attendance.class_date >= today
            is_planned = attendance.status == AttendanceStatus.PLANNED.value

            item = MeClassItem(
                attendance_id=attendance.id,
                class_session_id=session.id,
                class_date=attendance.class_date,
                start_time=session.start_time,
                end_time=session.end_time,
                status=attendance.status,
            )

            if is_planned and is_future_or_today:
                upcoming.append(item)
            else:
                history.append(item)

        return MeClassesResponse(upcoming=upcoming, history=history)

    # ---------- Календарь ----------

    def get_my_calendar(
        self,
        user: User,
        start_date: date,
        end_date: date,
    ) -> MeCalendarResponse:
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_date must be >= start_date",
            )

        stmt = (
            select(Attendance, ClassSession)
            .join(ClassSession, Attendance.class_session_id == ClassSession.id)
            .where(
                Attendance.user_id == user.id,
                Attendance.class_date >= start_date,
                Attendance.class_date <= end_date,
            )
            .order_by(Attendance.class_date, ClassSession.start_time)
        )

        rows = self.db.execute(stmt).all()

        days_map: dict[date, list[MeCalendarClassItem]] = {}

        for attendance, session in rows:
            item = MeCalendarClassItem(
                attendance_id=attendance.id,
                class_session_id=session.id,
                class_date=attendance.class_date,
                start_time=session.start_time,
                end_time=session.end_time,
                status=attendance.status,
            )
            days_map.setdefault(attendance.class_date, []).append(item)

        days: list[MeCalendarDay] = [
            MeCalendarDay(date=d, classes=cls)
            for d, cls in sorted(days_map.items(), key=lambda kv: kv[0])
        ]

        return MeCalendarResponse(
            start_date=start_date,
            end_date=end_date,
            days=days,
        )

    # ---------- Бронирование ----------

    def book_class(
        self,
        user: User,
        payload: ClassBookingRequest,
    ) -> MeClassItem:
        cs = self.db.get(ClassSession, payload.class_session_id)
        if cs is None or not cs.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ClassSession not found or inactive",
            )

        # 1) Дата должна совпадать с weekday занятия
        if payload.class_date.weekday() != cs.weekday:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="class_date does not match class_session weekday",
            )

        # 2) Нельзя записаться дважды на тот же класс/дату
        exists_stmt = select(Attendance.id).where(
            Attendance.user_id == user.id,
            Attendance.class_session_id == cs.id,
            Attendance.class_date == payload.class_date,
        )
        if self.db.scalar(exists_stmt) is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already booked for this class and date",
            )

        # 3) Проверка capacity (считаем все, кроме CANCELED)
        count_stmt = select(func.count(Attendance.id)).where(
            Attendance.class_session_id == cs.id,
            Attendance.class_date == payload.class_date,
            Attendance.status != AttendanceStatus.CANCELED.value,
        )
        current_count = self.db.scalar(count_stmt) or 0
        if current_count >= cs.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Class is full",
            )

        # 4) Пока membership не трогаем — membership_id=None
        attendance = Attendance(
            user_id=user.id,
            class_session_id=cs.id,
            membership_id=None,
            class_date=payload.class_date,
            status=AttendanceStatus.PLANNED.value,
        )
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)

        return MeClassItem(
            attendance_id=attendance.id,
            class_session_id=cs.id,
            class_date=attendance.class_date,
            start_time=cs.start_time,
            end_time=cs.end_time,
            status=attendance.status,
        )

    # ---------- Отмена ----------

    def cancel_class(
        self,
        user: User,
        payload: ClassCancelRequest,
    ) -> MeClassItem:
        stmt = (
            select(Attendance, ClassSession)
            .join(ClassSession, Attendance.class_session_id == ClassSession.id)
            .where(
                Attendance.id == payload.attendance_id,
                Attendance.user_id == user.id,
            )
        )
        row = self.db.execute(stmt).first()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance not found",
            )

        attendance, session = row

        # Нельзя отменить уже посещённое занятие
        if attendance.status == AttendanceStatus.ATTENDED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel already attended class",
            )

        # Если ещё не CANCELED — ставим CANCELED (идемпотентность) 
        if attendance.status != AttendanceStatus.CANCELED.value:
            attendance.status = AttendanceStatus.CANCELED.value
            self.db.add(attendance)
            self.db.commit()
            self.db.refresh(attendance)

        return MeClassItem(
            attendance_id=attendance.id,
            class_session_id=session.id,
            class_date=attendance.class_date,
            start_time=session.start_time,
            end_time=session.end_time,
            status=attendance.status,
        )
