from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.studio_settings import StudioSettings
from app.schemas.studio_settings import StudioSettingsUpdate
from app.core.exceptions import AppError  


class StudioSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get(self) -> StudioSettings:
        obj = self.db.scalar(select(StudioSettings).where(StudioSettings.id == 1))
        if obj is None:
            obj = StudioSettings(id=1)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
        return obj

    def update(self, payload: StudioSettingsUpdate) -> StudioSettings:
        obj = self.get()
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
