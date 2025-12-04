"""add user_id to leads

Revision ID: deec30786f53
Revises: 4954ef89053d
Create Date: 2025-11-28 04:01:49.458827

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'deec30786f53'
down_revision: Union[str, Sequence[str], None] = '4954ef89053d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Получаем список колонок в таблице leads
    columns = [col["name"] for col in inspector.get_columns("leads")]

    # Если user_id уже есть — НИЧЕГО не делаем
    if "user_id" in columns:
        return

    # Иначе добавляем колонку
    op.add_column(
        "leads",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    # FK под SQLite не делаем (чтобы не ловить NotImplementedError)
    # Для Postgres можно будет сделать отдельную миграцию.


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("leads")]

    if "user_id" in columns:
        op.drop_column("leads", "user_id")