# app/repositories/membership_repo.py

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.membership import MembershipPlan


class MembershipRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(
        self,
        location_id: Optional[int] = None,
        only_active: bool = True,  # на будущее, сейчас не используется
    ) -> List[MembershipPlan]:
        """
        Универсальный метод:
        - без параметров → вернёт все абонементы,
        - location_id=N → фильтрация по локации.
        Параметр only_active пока не используется, потому что
        у модели MembershipPlan нет поля is_active.
        """
        query = self.db.query(MembershipPlan)

        if location_id is not None:
            query = query.filter(MembershipPlan.location_id == location_id)

        # ВАЖНО: здесь НЕ фильтруем по MembershipPlan.is_active,
        # потому что такого поля в модели нет.
        # if only_active:
        #     query = query.filter(MembershipPlan.is_active == True)

        return query.all()

    def list_for_location(
        self,
        location_id: int,
        only_active: bool = True,
    ) -> List[MembershipPlan]:
        """
        Обёртка для читаемости: все тарифы для одной локации.
        """
        return self.list_all(location_id=location_id, only_active=only_active)

    def get_by_id(self, plan_id: int) -> Optional[MembershipPlan]:
        """
        Получить один тариф по id. Возвращает None, если не найден.
        """
        return self.db.query(MembershipPlan).get(plan_id)

    def create(self, data: dict) -> MembershipPlan:
        """
        Создать новый тариф (для будущей админки).
        """
        plan = MembershipPlan(**data)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def delete(self, plan_id: int) -> None:
        """
        Удалить тариф, если существует.
        """
        plan = self.db.query(MembershipPlan).get(plan_id)
        if plan is not None:
            self.db.delete(plan)
            self.db.commit()
