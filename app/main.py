# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import public, admin_leads
from app.db.base import Base
from app.db.session import engine

# Создаём таблицы при старте (для разработки это ок)
Base.metadata.create_all(bind=engine)

# Главное приложение FastAPI
app = FastAPI(
    title="Cohai Stretching API",
    version="0.1.0",
)

# CORS (пока разрешаем всё, потом ограничим доменом фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/", tags=["meta"])
def root():
    """
    Простой корневой эндпоинт.
    Удобен как health-check и подсказка, где искать документацию.
    """
    return {
        "app": "Cohai Stretchching API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_prefix": "/api/v1",
    }

# Регистрируем роутеры
app.include_router(public.router, prefix="/api/v1")
app.include_router(admin_leads.router, prefix="/api/v1")
