# app/core/logging.py

import logging
import logging.config
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Можно управлять поведением логирования через переменные окружения
LOG_LEVEL = os.getenv("COHAI_LOG_LEVEL", "INFO").upper()
LOG_TO_CONSOLE = os.getenv("COHAI_LOG_TO_CONSOLE", "1") == "1"

MAX_BYTES = int(os.getenv("COHAI_LOG_MAX_BYTES", 5 * 1024 * 1024))  # 5 MB
BACKUP_COUNT = int(os.getenv("COHAI_LOG_BACKUP_COUNT", 5))          # 5 файлов истории


class OneLineFormatter(logging.Formatter):
    """
    Форматтер без переносов строк внутри сообщений.
    Удобно, когда логи потом парсятся внешними системами.
    """
    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        return msg.replace("\n", "\\n")


def get_logging_config() -> dict:
    """
    Возвращает dictConfig для logging.
    Здесь задаются все хендлеры/форматтеры/логгеры.
    """
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers = {
        "file_info": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "app.log"),
            "maxBytes": MAX_BYTES,
            "backupCount": BACKUP_COUNT,
            "encoding": "utf-8",
            "level": "INFO",
            "formatter": "default",
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "error.log"),
            "maxBytes": MAX_BYTES,
            "backupCount": BACKUP_COUNT,
            "encoding": "utf-8",
            "level": "WARNING",
            "formatter": "default",
        },
    }

    if LOG_TO_CONSOLE:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "default",
        }

    # базовая конфигурация
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": OneLineFormatter,
                "format": fmt,
                "datefmt": datefmt,
            },
        },
        "handlers": handlers,
        "loggers": {
            # главный логгер приложения
            "cohai": {
                "level": LOG_LEVEL,
                "handlers": list(handlers.keys()),
                "propagate": False,
            },
        },
        # корневой логгер (на всякий случай)
        "root": {
            "level": LOG_LEVEL,
            "handlers": list(h for h in handlers.keys() if h != "file_error"),
        },
    }

    return config


def setup_logging() -> logging.Logger:
    """
    Инициализация логирования:
    - app.log   — INFO и выше
    - error.log — WARNING и выше
    - консоль (если включена)
    """
    logging.config.dictConfig(get_logging_config())
    logger = logging.getLogger("cohai")
    logger.info("Logging initialized (level=%s)", LOG_LEVEL)
    return logger
