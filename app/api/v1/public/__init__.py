# app/api/v1/public/__init__.py
from fastapi import APIRouter

# Один общий роутер для всех public-ручек
router = APIRouter(tags=["public"])

# Импортируем модули, чтобы они повесили свои ручки на router
from . import locations  # noqa: F401
from . import program_types  # noqa: F401
from . import schedule  # noqa: F401
from . import memberships  # noqa: F401
from . import leads  # noqa: F401
