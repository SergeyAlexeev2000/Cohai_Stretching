# app/api/v1/trainer/__init__.py
from fastapi import APIRouter

router = APIRouter()

from . import trainer_leads  # noqa: F401

router.include_router(trainer_leads.router)
