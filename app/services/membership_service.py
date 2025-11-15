# app/services/membership_service.py

from sqlalchemy.orm import Session

from app.repositories.membership_repo import MembershipRepository


class MembershipService:
    """
    Сервис для работы с тарифами / абонементами (MembershipPlan).
    Оборачивает репозиторий и инкапсулирует бизнес-логику.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = MembershipRepository(db)

    def list_for_location(self, location_id: int):
        """
        Вернуть список тарифов для конкретной локации.
        Используется в публичном endpoint'е /memberships.
        """
        return self.repo.list_for_location(location_id)

    # Дополнительно можно держать вспомогательные методы —
    # они не помешают, даже если пока нигде не вызываются.

    def list_all(self):
        """Все тарифы по всем локациям."""
        return self.repo.list_all()

    def get(self, plan_id: int):
        """Получить один тариф по id."""
        return self.repo.get(plan_id)

    def create(self, data):
        """Создать новый тариф (если потребуется админ-панель)."""
        return self.repo.create(data)

    def delete(self, plan_id: int):
        """Удалить тариф."""
        return self.repo.delete(plan_id)

