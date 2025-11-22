# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import global_exception_handler
from app.api.v1.public import router as public_router
from app.api.v1 import public, admin_leads
from app.db.base import Base  # пригодится для Alembic / init схемы
from app.db.session import engine

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

# Публичные эндпоинты
app.include_router(public.router, prefix="/api/v1")

# Админские эндпоинты по лидам
app.include_router(admin_leads.router, prefix="/api/v1/admin/leads")

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