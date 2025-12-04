"""Add user_id to trainers

Revision ID: 5151f9ecbb5e
Revises: 2b06bc1fb6c1
Create Date: 2025-11-30 23:54:10.131439

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5151f9ecbb5e'
down_revision: Union[str, Sequence[str], None] = '2b06bc1fb6c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # batch mode — Alembic сам создаст временную таблицу trainers_tmp,
    # добавит колонку и FK, скопирует данные, переименует обратно.
    with op.batch_alter_table("trainers", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("user_id", sa.Integer(), nullable=True),
        )
        batch_op.create_foreign_key(
            "fk_trainers_user_id_users",
            "users",           # referent_table
            ["user_id"],       # local_cols
            ["id"],            # remote_cols
        )


def downgrade() -> None:
    # Обратная операция тоже через batch
    with op.batch_alter_table("trainers", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_trainers_user_id_users",
            type_="foreignkey",
        )
        batch_op.drop_column("user_id")