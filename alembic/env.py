from __future__ import annotations

from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import pool, engine_from_config

# ===== A. Настройка sys.path, чтобы работал import app.* =====

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[1]  # .../alembic/env.py -> корень проекта

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Теперь можно импортировать наше приложение
from app.db.base import Base
from app.db.session import engine

# Импортируем все модули с моделями, чтобы они зарегистрировались в Base.metadata
from app.models import location  # noqa: F401
from app.models import location_area  # noqa: F401
from app.models import program_type  # noqa: F401
from app.models import membership  # noqa: F401
from app.models import trainer  # noqa: F401
from app.models import class_session  # noqa: F401
from app.models import lead  # noqa: F401

# ===== B. Стандартная часть Alembic =====

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Очень важно: сюда кладём metadata всех моделей
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Используем тот же URL, что и у нашего engine
    url = str(engine.url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Используем именно наш engine из app.db.session
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
