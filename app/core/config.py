# app/core/config.py

from __future__ import annotations

import os
from typing import List


class Settings:
    """
    Центральная конфигурация приложения.

    Пока что значения захардкожены, но уже есть задел
    на чтение из переменных окружения.
    """

    # Имя и версия приложения
    APP_NAME: str = "Cohai Stretchchning API"
    APP_VERSION: str = "0.1.0"

    # CORS: какие origin-ы разрешены фронтенду
    # Можно переопределить переменной окружения:
    # BACKEND_CORS_ORIGINS="http://localhost:3000,https://my-site.com"
    _cors_origins_env: str = os.getenv("BACKEND_CORS_ORIGINS", "*")

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        raw = self._cors_origins_env
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


# Один объект настроек на всё приложение
settings = Settings()