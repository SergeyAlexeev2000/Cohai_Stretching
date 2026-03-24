from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.api.v1.deps_auth import require_role
from app.models.user import UserRole
from app.schemas.studio_settings import StudioSettingsRead, StudioSettingsUpdate
from app.services.studio_settings_service import StudioSettingsService

router = APIRouter(
    prefix="/admin/studio-settings",
    tags=["admin_studio_settings"],
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.SUPERADMIN))],
)

@router.get("", response_model=StudioSettingsRead)
def get_settings(db: Session = Depends(get_db)):
    return StudioSettingsService(db).get()

@router.patch("", response_model=StudioSettingsRead)
def update_settings(payload: StudioSettingsUpdate, db: Session = Depends(get_db)):
    return StudioSettingsService(db).update(payload)
