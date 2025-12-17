# app/services/class_session_service.py

from __future__ import annotations

from datetime import datetime, date, time
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError

from app.models.class_session import ClassSession
from app.models.location import Location
from app.models.program_type import ProgramType
from app.models.trainer import Trainer
from app.models.membership import MembershipPlan

from app.schemas.class_session import (
    ClassSessionCreate,
    ClassSessionUpdate,
)

from app.repositories.class_session_repo import ClassSessionRepository


def _validate_time_range(start: time, end: time) -> None:
    """Проверка, что время окончания позже начала."""
    dt_start = datetime.combine(date.today(), start)
    dt_end = datetime.combine(date.today(), end)
    if dt_end <= dt_start:
        raise AppError(
            code="INVALID_TIME_RANGE",
            message="end_time must be later than start_time",
            http_status=400,
        )


class ClassSessionService:
    """Бизнес-логика для расписания (class_sessions) в админке."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ClassSessionRepository(db)


    # --- вспомогательное: проверки внешних ключей ---

    def _ensure_fk_exists(
        self,
        model,
        obj_id: int,
        *,
        code: str,
        field: str,
    ) -> None:
        """
        Универсальная проверка существования объекта с id=obj_id
        для Location/ProgramType/Trainer/MembershipPlan.
        """
        instance = self.db.scalar(select(model).where(model.id == obj_id))
        if instance is None:
            raise AppError(
                code=code,
                message=f"{model.__name__} with id={obj_id} not found",
                http_status=404,
                extra={field: obj_id},
            )
        
    
    # --- базовые операции ---

    def list_all(
        self,
        *,
        location_id: Optional[int] = None,
        program_type_id: Optional[int] = None,
        weekday: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> List[ClassSession]:
        """
        Список занятий с фильтрами.

        Фильтры все опциональные.
        """
        return self.repo.list_all(
            location_id=location_id,
            program_type_id=program_type_id,
            weekday=weekday,
            is_active=is_active,
        )

    def get_or_404(self, session_id: int) -> ClassSession:
        """Вернуть занятие или 404."""
        obj = self.repo.get(session_id)
        if obj is None:
            raise AppError(
                code="CLASS_SESSION_NOT_FOUND",
                message=f"ClassSession with id={session_id} not found",
                http_status=404,
                extra={"class_session_id": session_id},
            )
        return obj

    # --- Валидации ---

    def _validate_time_range(
        self,
        weekday: int,
        start_time: time,
        end_time: time,
    ) -> None:
        if weekday < 0 or weekday > 6:
            raise AppError(
                code="INVALID_WEEKDAY",
                message="weekday must be in range [0, 6]",
                http_status=400,
                extra={"weekday": weekday},
            )

        if end_time <= start_time:
            raise AppError(
                code="INVALID_TIME_RANGE",
                message="end_time must be after start_time",
                http_status=400,
                extra={
                    "start_time": str(start_time),
                    "end_time": str(end_time),
                },
            )

    def _validate_related_ids(
        self,
        *,
        location_id: int,
        program_type_id: int,
        trainer_id: int,
        membership_plan_id: Optional[int],
    ) -> None:
        """
        Проверяем, что все связанные сущности существуют
        и что абонемент (если есть) относится к локации.
        """

        # --- Location ---
        stmt_loc = select(Location).where(Location.id == location_id)
        location = self.db.scalars(stmt_loc).first()
        if location is None:
            raise AppError(
                code="LOCATION_NOT_FOUND",
                message=f"Location with id={location_id} not found",
                http_status=404,
                extra={"location_id": location_id},
            )

        # --- ProgramType ---
        stmt_prog = select(ProgramType).where(ProgramType.id == program_type_id)
        program_type = self.db.scalars(stmt_prog).first()
        if program_type is None:
            raise AppError(
                code="PROGRAM_TYPE_NOT_FOUND",
                message=f"ProgramType with id={program_type_id} not found",
                http_status=404,
                extra={"program_type_id": program_type_id},
            )

        # --- Trainer ---
        stmt_trainer = select(Trainer).where(Trainer.id == trainer_id)
        trainer = self.db.scalars(stmt_trainer).first()
        if trainer is None:
            raise AppError(
                code="TRAINER_NOT_FOUND",
                message=f"Trainer with id={trainer_id} not found",
                http_status=404,
                extra={"trainer_id": trainer_id},
            )

        # --- MembershipPlan (опционально) ---
        if membership_plan_id is not None:
            stmt_plan = select(MembershipPlan).where(
                MembershipPlan.id == membership_plan_id
            )
            plan = self.db.scalars(stmt_plan).first()
            if plan is None:
                raise AppError(
                    code="MEMBERSHIP_NOT_FOUND",
                    message=f"MembershipPlan with id={membership_plan_id} not found",
                    http_status=404,
                    extra={"membership_plan_id": membership_plan_id},
                )

            # Дополнительная бизнес-проверка: абонемент должен относиться к той же локации
            if plan.location_id != location_id:
                raise AppError(
                    code="MEMBERSHIP_LOCATION_MISMATCH",
                    message=(
                        "MembershipPlan location does not match ClassSession location"
                    ),
                    http_status=400,
                    extra={
                        "location_id": location_id,
                        "plan_location_id": plan.location_id,
                        "membership_plan_id": membership_plan_id,
                    },
                )
            

    # --- CRUD ---

    def create(self, payload: ClassSessionCreate) -> ClassSession:
        """Создать занятие."""
        _validate_time_range(payload.start_time, payload.end_time)
        if payload.capacity <= 0:
            raise AppError(
                code="INVALID_CAPACITY",
                message="capacity must be positive",
                http_status=400,
            )

        # capacity > 0
        if payload.capacity <= 0:
            raise AppError(
                code="INVALID_CAPACITY",
                message="capacity must be positive",
                http_status=400,
            )

        # проверки внешних ключей
        self._ensure_fk_exists(
            Location,
            payload.location_id,
            code="LOCATION_NOT_FOUND",
            field="location_id",
        )
        self._ensure_fk_exists(
            ProgramType,
            payload.program_type_id,
            code="PROGRAM_TYPE_NOT_FOUND",
            field="program_type_id",
        )
        self._ensure_fk_exists(
            Trainer,
            payload.trainer_id,
            code="TRAINER_NOT_FOUND",
            field="trainer_id",
        )
        if payload.membership_plan_id is not None:
            self._ensure_fk_exists(
                MembershipPlan,
                payload.membership_plan_id,
                code="MEMBERSHIP_PLAN_NOT_FOUND",
                field="membership_plan_id",
            )
        
        obj = ClassSession(
            weekday=payload.weekday,
            start_time=payload.start_time,
            end_time=payload.end_time,
            location_id=payload.location_id,
            program_type_id=payload.program_type_id,
            trainer_id=payload.trainer_id,
            membership_plan_id=payload.membership_plan_id,
            capacity=payload.capacity,
            is_active=payload.is_active,
        )
        self.repo.create(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, session_id: int, payload: ClassSessionUpdate) -> ClassSession:
        """Частично обновить занятие."""
        obj = self.get_or_404(session_id)

        data = payload.model_dump(exclude_unset=True)

        # сначала проверим время, если оно меняется
        new_start = data.get("start_time", obj.start_time)
        new_end = data.get("end_time", obj.end_time)
        if ("start_time" in data) or ("end_time" in data):
            _validate_time_range(new_start, new_end)

        # capacity (если явно прислали)
        if "capacity" in data and data["capacity"] is not None:
            if data["capacity"] <= 0:
                raise AppError(
                    code="INVALID_CAPACITY",
                    message="capacity must be positive",
                    http_status=400,
                )

        # проверки внешних ключей, только если поле реально меняют
        if "location_id" in data:
            self._ensure_fk_exists(
                Location,
                data["location_id"],
                code="LOCATION_NOT_FOUND",
                field="location_id",
            )

        if "program_type_id" in data:
            self._ensure_fk_exists(
                ProgramType,
                data["program_type_id"],
                code="PROGRAM_TYPE_NOT_FOUND",
                field="program_type_id",
            )

        if "trainer_id" in data:
            self._ensure_fk_exists(
                Trainer,
                data["trainer_id"],
                code="TRAINER_NOT_FOUND",
                field="trainer_id",
            )

        if "membership_plan_id" in data and data["membership_plan_id"] is not None:
            self._ensure_fk_exists(
                MembershipPlan,
                data["membership_plan_id"],
                code="MEMBERSHIP_PLAN_NOT_FOUND",
                field="membership_plan_id",
            )
        

        for field, value in data.items():
            setattr(obj, field, value)

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj


    def cancel(self, session_id: int) -> ClassSession:
        """
        Отменить занятие: пометить как неактивное (is_active = False)
        и вернуть обновлённый объект.
        """
        obj = self.get_or_404(session_id)

        # Если занятие уже отменено — просто возвращаем как есть (идемпотентность).
        if not obj.is_active:
            return obj

        obj.is_active = False
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, session_id: int) -> None:
        """Удалить занятие."""
        obj = self.get_or_404(session_id)
        self.repo.delete(obj)
        self.db.commit()

    # --- Совместимость с существующими роутерами (shim-методы) ---

    def create_session(self, payload: ClassSessionCreate) -> ClassSession:
        """
        Shim для старого имени метода, используемого в роутерах.
        """
        return self.create(payload)

    def update_session(self, session_id: int, payload: ClassSessionUpdate) -> ClassSession:
        """
        Shim для старого имени метода.
        """
        return self.update(session_id, payload)

    def delete_session(self, session_id: int) -> None:
        """
        Shim для старого имени метода.
        """
        return self.delete(session_id)

    def list_sessions(
        self,
        *,
        location_id: Optional[int] = None,
        program_type_id: Optional[int] = None,
        weekday: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> List[ClassSession]:
        """
        Shim для старого имени метода.
        """
        return self.list_all(
            location_id=location_id,
            program_type_id=program_type_id,
            weekday=weekday,
            is_active=is_active,
        )

    def list_sessions_admin(
        self,
        *,
        location_id: Optional[int] = None,
        program_type_id: Optional[int] = None,
        weekday: Optional[int] = None,
        trainer_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> List[ClassSession]:
        """
        Shim: повторяет сигнатуру роутера. Аргументы trainer_id и include_inactive
        пока не используются в бизнес-логике, но должны приниматься.
        """
        return self.list_all(
            location_id=location_id,
            program_type_id=program_type_id,
            weekday=weekday,
            # include_inactive пока не реализуем — роут будет работать без него
            is_active=None if include_inactive else True,
        )

    def get_session(self, session_id: int) -> ClassSession:
        """
        Shim-метод для совместимости с роутером:
        старое имя метода — get_session, под капотом используем get_or_404.
        """
        return self.get_or_404(session_id)

