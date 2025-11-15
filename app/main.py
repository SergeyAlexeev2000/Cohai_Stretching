# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import public, admin_leads
from app.db.base import Base
from app.db.session import engine

from app.core.exceptions import global_exception_handler   # <-- импорт хендлера
from fastapi import Request, Depends
from fastapi.responses import JSONResponse


app = FastAPI(
    title="Cohai Stretching API",
    version="0.1.0",
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTERS ---
app.include_router(public.router, prefix="/api/v1")
app.include_router(admin_leads.router, prefix="/api/v1")

# --- GLOBAL ERROR HANDLER ---
app.add_exception_handler(Exception, global_exception_handler)


# --- ROOT ENDPOINT ---
@app.get("/", tags=["meta"])
def root():
    return {
        "app": "Cohai Stretchchinng API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }