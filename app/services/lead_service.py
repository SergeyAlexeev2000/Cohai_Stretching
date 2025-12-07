# app/services/lead_service.py

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.exceptions import AppError
from app.models.lead import Lead, LeadStatus
from app.models.user import User
from app.schemas.lead import LeadCreateGuestVisit, LeadUpdateAdmin
from app.repositories.lead_repo import LeadRepository


class LeadService:
    """Работа с лидами (заявками). Слой бизнес-логики над LeadRepository."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = LeadRepository(db)

    # ---------- Админские выборки ----------

    def list_leads_for_admin(
        self,
        *,
        status: LeadStatus | None = None,
        trainer_id: int | None = None,
    ) -> list[Lead]:
        """
        Список лидов для админа с фильтрами по статусу и назначенному тренеру.
        """
        return self.repo.list_for_admin(status=status, trainer_id=trainer_id)

    def list_leads_for_trainer(
        self,
        trainer_id: int,
        *,
        status: LeadStatus | None = None,
    ) -> list[Lead]:
        """
        Список лидов, назначенных конкретному тренеру.
        """
        stmt = (
            select(Lead)
            .where(Lead.assigned_trainer_id == trainer_id)
            .order_by(Lead.created_at.desc())
        )

        if status is not None:
            stmt = stmt.where(Lead.status == status)

        return list(self.db.scalars(stmt).all())

    def list_leads(
        self,
        *,
        is_processed: Optional[bool] = None,
        location_id: Optional[int] = None,
        program_type_id: Optional[int] = None,
        query: Optional[str] = None,
    ) -> List[Lead]:
        """
        Список лидов для админки с расширенными фильтрами.

        Параметры:
        - is_processed: True / False / None
        - location_id: фильтр по локации
        - program_type_id: фильтр по типу программы
        - query: подстрочный поиск по full_name / phone / source / message
        """
        stmt = select(Lead).order_by(Lead.created_at.desc())

        if is_processed is not None:
            stmt = stmt.where(Lead.is_processed == is_processed)

        if location_id is not None:
            stmt = stmt.where(Lead.location_id == location_id)

        if program_type_id is not None:
            stmt = stmt.where(Lead.program_type_id == program_type_id)

        if query:
            pattern = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Lead.full_name).like(pattern),
                    func.lower(Lead.phone).like(pattern),
                    func.lower(Lead.source).like(pattern),
                    func.lower(Lead.message).like(pattern),
                )
            )

        return list(self.db.scalars(stmt).all())

    # ---------- Общие операции над одним лидом ----------

    def get_lead(self, lead_id: int) -> Lead:
        """Вернуть один лид или кинуть 404 через AppError."""
        lead = self.repo.get(lead_id)
        if lead is None:
            raise AppError(
                code="LEAD_NOT_FOUND",
                message=f"Lead with id={lead_id} not found",
                http_status=404,
                extra={"lead_id": lead_id},
            )
        return lead

    def _get_or_404(self, lead_id: int) -> Lead:
        """Внутренний метод: 404, если лида нет (формат ошибки попроще)."""
        lead = self.repo.get(lead_id)
        if not lead:
            # такой вариант у тебя уже был — оставляем для совместимости
            raise AppError(f"Lead with id={lead_id} not found")
        return lead

    def mark_processed(self, lead_id: int) -> Lead:
        """
        Пометить лид как обработанный.
        Если уже обработан – просто возвращаем.
        """
        lead = self.get_lead(lead_id)

        if not lead.is_processed:
            lead.is_processed = True
            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)

        return lead

    def update_lead_admin(self, lead_id: int, data: LeadUpdateAdmin) -> Lead:
        """
        Обновление лида админом:
        - status
        - assigned_trainer_id
        - assigned_admin_id
        и т.п.
        """
        lead = self._get_or_404(lead_id)

        if data.status is not None:
            lead.status = data.status

        if data.assigned_trainer_id is not None:
            lead.assigned_trainer_id = data.assigned_trainer_id

        if data.assigned_admin_id is not None:
            lead.assigned_admin_id = data.assigned_admin_id

        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def delete_lead(self, lead_id: int) -> None:
        """Удалить лид (жёстко) или 404, если не найден."""
        lead = self.get_lead(lead_id)
        self.repo.delete(lead)
        self.db.commit()

    # ---------- PUBLIC: создание гостевого визита ----------

    def create_guest_visit(
        self,
        payload: LeadCreateGuestVisit,
        user: Optional[User] = None,
    ) -> Lead:
        """
        Создать лид для гостевого визита.
        Если передан user — привязываем заявку к этому пользователю.
        """
        lead = Lead(
            full_name=payload.full_name,
            phone=payload.phone,
            source="guest_visit",
            location_id=payload.location_id,
            program_type_id=payload.program_type_id,
            is_processed=False,
            user_id=user.id if user is not None else None,
        )
        # используем репозиторий для create
        self.repo.create(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    # ---------- ME: лиды пользователя (на будущее / под me/leads) ----------

    def list_for_user(self, user: User) -> List[Lead]:
        """Вернуть все лиды, связанные с пользователем (для /me/leads)."""
        return self.repo.list_by_user(user.id)
