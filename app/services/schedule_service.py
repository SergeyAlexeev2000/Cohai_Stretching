# app/services/schedule_service.py

from sqlalchemy.orm import Session

from app.repositories.class_session_repo import ClassSessionRepository


class ScheduleService:
    """
    Сервис для работы с расписанием (ClassSession).

    Сейчас минимальная версия: только то, что нужно для
    публичного эндпоинта /schedule.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = ClassSessionRepository(db)

    def get_schedule_for_location(self, location_id: int):
        """
        Вернуть список занятий для конкретной локации.

        Используется в:
            app.api.v1.public.get_schedule()
        """
        # Если в репозитории есть более подходящий метод — можно
        # использовать его. Пока делаем типовую заглушку.
        return self.repo.list_for_location(location_id)
        # Если такого метода нет, можно временно сделать, например:
        # return self.repo.list_all_for_location(location_id)
        # или даже:
        # return self.repo.list_all()
