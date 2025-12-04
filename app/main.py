# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import global_exception_handler

from app.api.v1.public import router as public_router
from app.api.v1.admin_leads import router as admin_leads_router
from app.api.v1.admin_memberships import router as admin_memberships_router
from app.api.v1.admin_locations import router as admin_locations_router
from app.api.v1.admin_class_sessions import router as admin_class_sessions_router
from app.api.v1.auth import router as auth_router
from app.api.v1.me import router as me_router
from app.api.v1.trainer_leads import router as trainer_leads_router

from app.db.base import Base  # пригодится для Alembic / init схемы
from app.db.session import engine

# ВАЖНО: импортируем все модели, чтобы SQLAlchemy увидел все классы
# и смог разрешить строки типа "Trainer", "ClassSession" и т.д.
from app.models import location          # noqa: F401
from app.models import location_area     # noqa: F401
from app.models import program_type      # noqa: F401
from app.models import membership        # noqa: F401
from app.models import trainer           # noqa: F401
from app.models import class_session     # noqa: F401
from app.models import lead              # noqa: F401

# Инициализируем логирование ПЕРЕД созданием приложения
logger = setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# --- CORS ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Роуты v1 ---

# Публичные эндпоинты доступны И так, и так:
#   /public/...
#   /api/v1/...
app.include_router(public_router, prefix="/public")
app.include_router(public_router, prefix="/api/v1")

# Админские эндпоинты по лидам
app.include_router(admin_leads_router, prefix="/api/v1")

# Админские эндпоинты по тарифам/абонементам
app.include_router(admin_memberships_router, prefix="/api/v1")

# Админские эндпоинты по локациям
app.include_router(admin_locations_router, prefix="/api/v1")

# Админ: занятия (class_sessions)
app.include_router(admin_class_sessions_router, prefix="/api/v1")

# Эндпоинты аутентификации и регистрации
app.include_router(auth_router, prefix="/api/v1")

# Эндпоинты "Мой профиль"
app.include_router(me_router, prefix="/api/v1")

# Эндпоинты тренера по лидам
app.include_router(trainer_leads_router, prefix="/api/v1")


# Логирование
logger.info("Application startup: loading routes")

# --- Глобальный обработчик ошибок ---

# Один раз регистрируем глобальный обработчик на все непойманные Exception
app.add_exception_handler(Exception, global_exception_handler)


# --- Корневой эндпоинт (health / meta) ---

@app.get("/", tags=["meta"])
def root():
    """
    Простой корневой эндпоинт.

    Удобен как health-check и как подсказка,
    где искать документацию по API.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }