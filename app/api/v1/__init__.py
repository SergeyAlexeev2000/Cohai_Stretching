# app/api/v1/__init__.py
from fastapi import APIRouter

from . import auth
from .public import router as public_router
from .me import router as me_router
from .admin import router as admin_router
from .trainer import router as trainer_router

api_router = APIRouter()

# auth
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# public
api_router.include_router(public_router)

# me
api_router.include_router(me_router)

# admin
api_router.include_router(admin_router)

# trainer
api_router.include_router(trainer_router)

__all__ = ["api_router"]
