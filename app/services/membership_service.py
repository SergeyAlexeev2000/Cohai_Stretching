# app/services/membership_service.py
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.membership import MembershipPlan
from app.repositories.membership_repo import MembershipRepository


class MembershipService:
    """
    Сервис для работы с тарифами / абонементами (MembershipPlan).
    Оборачивает репозиторий и инкапсулирует бизнес-логику.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = MembershipRepository(db)

    def list_for_location(
        self,
        location_id: int,
        only_active: bool = True,
    ) -> List[MembershipPlan]:
        """
        Вернуть список тарифов для конкретной локации.
        Используется в публичном endpoint'е /memberships.
        """
        return self.repo.list_all(location_id=location_id, only_active=only_active)

    def list_all(
        self,
        location_id: Optional[int] = None,
        only_active: bool = True,
    ) -> List[MembershipPlan]:
        """
        Все тарифы:
        - если location_id=None — по всем локациям,
        - если передан location_id — только по конкретной локации,
        - only_active=True — только активные тарифы (для публичного API).
        """
        return self.repo.list_all(location_id=location_id, only_active=only_active)

    def get(self, plan_id: int) -> Optional[MembershipPlan]:
        """
        Получить один тариф по id.
        Возвращает None, если не найден.
        """
        return self.repo.get_by_id(plan_id)

    def create(self, data):
        """Заготовка под создание тарифа (для будущей админ-панели)."""
        raise NotImplementedError("Создание тарифов ещё не реализовано")

    def delete(self, plan_id: int):
        """Заготовка под удаление тарифа (для будущей админ-панели)."""
        raise NotImplementedError("Удаление тарифов ещё не реализовано")