# app/core/exceptions.py
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("cohai")


class AppError(Exception):
    """
    Бизнес-ошибка приложения.

    code  – машинное имя (например, "LEAD_NOT_FOUND")
    message – человекочитаемое описание
    http_status – какой код отдать клиенту (обычно 400 / 404 / 422)
    extra – доп. данные (опционально)
    """

    def __init__(
        self,
        code: str,
        message: str,
        http_status: int = 400,
        extra: Dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        self.extra = extra or {}
        super().__init__(message)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Глобальный обработчик ошибок:

    * AppError          → аккуратный JSON + нужный статус
    * HTTPException     → как есть, но тоже логируем
    * Любая другая ошибка → 500 + лог со stacktrace
    """

    # 1) Наши бизнес-ошибки
    if isinstance(exc, AppError):
        logger.warning(
            "AppError %s on %s %s: %s",
            exc.code,
            request.method,
            request.url.path,
            exc.message,
        )

        payload: Dict[str, Any] = {
            "detail": exc.message,
            "code": exc.code,
        }
        if exc.extra:
            payload["extra"] = exc.extra

        return JSONResponse(
            status_code=exc.http_status,
            content=payload,
        )

    # 2) Стандартные HTTP-ошибки FastAPI
    if isinstance(exc, HTTPException):
        logger.info(
            "HTTPException %s on %s %s: %s",
            exc.status_code,
            request.method,
            request.url.path,
            exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None),
        )

    # 3) Любой неожиданный Exception → 500
    logger.exception(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
