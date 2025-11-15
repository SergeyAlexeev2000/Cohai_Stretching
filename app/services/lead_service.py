# app/services/lead_service.py

from sqlalchemy.orm import Session

from app.schemas.lead import LeadCreateGuestVisit
from app.repositories.lead_repo import LeadRepository
from app.models.lead import Lead


class LeadService:
    """
    Сервис для работы с лидами (запросы на гостевой визит, заявки и т.п.)
    Оборачивает репозиторий и выполняет бизнес-логику.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = LeadRepository(db)

    def create_guest_visit(self, payload: LeadCreateGuestVisit) -> Lead:
        """
        Создать запрос на гостевой визит.
        """
        # Здесь может быть бизнес-логика:
        # - проверка уникальности телефона
        # - проверка существования локации
        # - логирование
        # - отправка уведомлений и т.п.

        lead = self.repo.create_guest_visit(payload)
        return lead

    def get_all(self):
        """
        Получить всех лидов (например, для админ-панели).
        """
        return self.repo.get_all()

    def get(self, lead_id: int):
        return self.repo.get(lead_id)

    def delete(self, lead_id: int):
        return self.repo.delete(lead_id)