# app/api/v1/admin/__init__.py
from fastapi import APIRouter

router = APIRouter()

# Импортируем подмодули, чтобы они зарегистрировали свои роуты
from . import admin_locations  # noqa: F401
from . import admin_memberships  # noqa: F401
from . import admin_leads  # noqa: F401
from . import admin_class_sessions  # noqa: F401

# Подключаем их роутеры к общему router
router.include_router(admin_locations.router)
router.include_router(admin_memberships.router)
router.include_router(admin_leads.router)
router.include_router(admin_class_sessions.router)
