# app/api/v1/me/__init__.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/me",
    tags=["me"],
)

# Импортируем модули, чтобы они зарегистрировали свои ручки
from . import profile  # noqa: F401
from . import memberships  # noqa: F401
from . import leads  # noqa: F401
from . import classes  # noqa: F401
from . import calendar  # noqa: F401
from . import booking  # noqa: F401
