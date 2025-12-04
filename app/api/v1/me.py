# app/api/v1/me.py
from __future__ import annotations

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import get_current_user

from app.core.security import get_password_hash, verify_password

from app.models.lead import Lead
from app.models.user import User
from app.models.membership import Membership, MembershipStatus
from app.models.attendance import Attendance, AttendanceStatus
from app.models.class_session import ClassSession

from app.schemas.lead import LeadRead
from app.schemas.user_auth import ProfileOut, ProfileUpdateIn
from app.schemas.membership import MembershipRead, MembershipListResponse
from app.schemas.attendance import (
    MeClassItem,
    MeClassesResponse,
    ClassBookingRequest,
    ClassCancelRequest,
)
from app.schemas.calendar import MeCalendarClassItem, MeCalendarDay, MeCalendarResponse


router = APIRouter(
    prefix="/me",
    tags=["me"],
)


# ---------- Профиль ----------


@router.get("/profile", response_model=ProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Вернуть профиль текущего пользователя.
    """
    return current_user


@router.patch("/profile", response_model=ProfileOut)
def update_profile(
    payload: ProfileUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Обновить профиль текущего пользователя.

    Можно:
    - поменять full_name и phone;
    - при указании current_password + new_password — сменить пароль.
    """
    # Обновляем имя и телефон, если переданы
    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    if payload.phone is not None:
        current_user.phone = payload.phone

    # Логика смены пароля
    if payload.new_password is not None:
        if not payload.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to set a new password.",
            )

        if not verify_password(payload.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        current_user.password_hash = get_password_hash(payload.new_password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


# ---------- Мои абонементы ----------


@router.get("/memberships", response_model=MembershipListResponse)
def my_memberships(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MembershipListResponse:
    """
    Вернуть абонементы текущего пользователя, разделённые на:
    - active: действующие (status=ACTIVE и end_date >= сегодня)
    - history: истёкшие / отменённые / замороженные.
    """
    stmt = (
        select(Membership)
        .where(Membership.user_id == current_user.id)
        .order_by(Membership.start_date.desc())
    )
    memberships = list(db.scalars(stmt).all())

    today = date.today()
    active: list[MembershipRead] = []
    history: list[MembershipRead] = []

    for m in memberships:
        is_active_status = m.status == MembershipStatus.ACTIVE.value
        is_not_expired = m.end_date >= today
        target = active if (is_active_status and is_not_expired) else history

        target.append(MembershipRead.model_validate(m))

    return MembershipListResponse(active=active, history=history)


# ---------- Мои лиды ----------


@router.get("/leads", response_model=List[LeadRead])
def my_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Вернуть все лиды, связанные с текущим пользователем (lead.user_id = current_user.id).
    """
    stmt = (
        select(Lead)
        .where(Lead.user_id == current_user.id)
        .order_by(Lead.created_at.desc())
    )
    leads = db.scalars(stmt).all()
    return list(leads)


# ---------- Мои занятия -----------


@router.get("/classes", response_model=MeClassesResponse)
def my_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MeClassesResponse:
    """
    Мои занятия (записи на занятия), разбитые на:
    - upcoming: будущие занятия (PLANNED и class_date >= сегодня)
    - history: всё остальное (ATTENDED, MISSED, CANCELED, а также PLANNED в прошлом).
    """
    today = date.today()

    # Берём Attendance + ClassSession, чтобы иметь время занятия
    stmt = (
        select(Attendance, ClassSession)
        .join(ClassSession, Attendance.class_session_id == ClassSession.id)
        .where(Attendance.user_id == current_user.id)
        .order_by(Attendance.class_date, ClassSession.start_time)
    )

    rows = db.execute(stmt).all()

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

# ---------- Мой календарь -----------

@router.get("/calendar", response_model=MeCalendarResponse)
def my_calendar(
    start_date: date = Query(..., description="Начало диапазона (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Конец диапазона (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MeCalendarResponse:
    """
    Календарь пользователя за указанный период.

    Возвращает только те дни, в которые у пользователя есть записи (Attendance)
    в диапазоне [start_date, end_date].
    """
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be >= start_date",
        )

    stmt = (
        select(Attendance, ClassSession)
        .join(ClassSession, Attendance.class_session_id == ClassSession.id)
        .where(
            Attendance.user_id == current_user.id,
            Attendance.class_date >= start_date,
            Attendance.class_date <= end_date,
        )
        .order_by(Attendance.class_date, ClassSession.start_time)
    )

    rows = db.execute(stmt).all()

    # группируем по дате
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

# ---------- Бронирование / Отмена занятий -----------

@router.post("/classes/book", response_model=MeClassItem)
def book_class(
    payload: ClassBookingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MeClassItem:
    """
    Записаться на занятие (конкретная дата).
    Правила:
    - class_session должен существовать и быть is_active=True
    - date должен совпадать по weekday с class_session.weekday
    - нельзя записаться дважды на одно и то же занятие в одну и ту же дату
    - учитываем capacity (кол-во записей != CANCELED)
    """
    cs = db.get(ClassSession, payload.class_session_id)
    if cs is None or not cs.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ClassSession not found or inactive",
        )

    # Проверка соответствия дня недели (0=Monday,...,6=Sunday)
    if payload.class_date.weekday() != cs.weekday:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="class_date does not match class_session weekday",
        )

    # Уже записан?
    exists_stmt = select(Attendance.id).where(
        Attendance.user_id == current_user.id,
        Attendance.class_session_id == cs.id,
        Attendance.class_date == payload.class_date,
    )
    if db.scalar(exists_stmt) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already booked for this class and date",
        )

    # Проверка capacity (все записи, кроме CANCELED)
    count_stmt = select(func.count(Attendance.id)).where(
        Attendance.class_session_id == cs.id,
        Attendance.class_date == payload.class_date,
        Attendance.status != AttendanceStatus.CANCELED.value,
    )
    current_count = db.scalar(count_stmt) or 0
    if current_count >= cs.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Class is full",
        )

    # Пока membership не трогаем — можно будет привязать позже
    attendance = Attendance(
        user_id=current_user.id,
        class_session_id=cs.id,
        membership_id=None,
        class_date=payload.class_date,
        status=AttendanceStatus.PLANNED.value,
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return MeClassItem(
        attendance_id=attendance.id,
        class_session_id=cs.id,
        class_date=attendance.class_date,
        start_time=cs.start_time,
        end_time=cs.end_time,
        status=attendance.status,
    )


@router.post("/classes/cancel", response_model=MeClassItem)
def cancel_class(
    payload: ClassCancelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MeClassItem:
    """
    Отмена своей записи на занятие.
    Правила:
    - можно отменить только свою запись
    - если уже CANCELED — возвращаем как есть (idempotent)
    - если ATTENDED — запрещаем отмену
    """
    stmt = (
        select(Attendance, ClassSession)
        .join(ClassSession, Attendance.class_session_id == ClassSession.id)
        .where(
            Attendance.id == payload.attendance_id,
            Attendance.user_id == current_user.id,
        )
    )
    row = db.execute(stmt).first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance not found",
        )

    attendance, session = row

    if attendance.status == AttendanceStatus.ATTENDED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel already attended class",
        )

    # idempotent: если уже отменён — просто вернём
    if attendance.status != AttendanceStatus.CANCELED.value:
        attendance.status = AttendanceStatus.CANCELED.value
        db.add(attendance)
        db.commit()
        db.refresh(attendance)

    return MeClassItem(
        attendance_id=attendance.id,
        class_session_id=session.id,
        class_date=attendance.class_date,
        start_time=session.start_time,
        end_time=session.end_time,
        status=attendance.status,
    )
