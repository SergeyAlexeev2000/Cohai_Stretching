from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import public, admin_leads
from app.db.base import Base
from app.db.session import engine


# ============================================================
# 1. Создаем приложение
# ============================================================
app = FastAPI(
    title="Cohai Stretching API",
    version="0.1.0",
)


# ============================================================
# 2. CORS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 3. Глобальный обработчик исключений
# ============================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error": str(exc),
        },
    )


# ============================================================
# 4. Подключение роутеров
# ============================================================
app.include_router(public.router, prefix="/api/v1")
app.include_router(admin_leads.router, prefix="/api/v1")


# ============================================================
# 5. Корневой эндпоинт
# ============================================================
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
    }
