"""Add message column to leads

Revision ID: 6cbb6e1faef6
Revises: b9a6b29d0915
Create Date: 2025-12-01 14:47:57.480559

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cbb6e1faef6'
down_revision: Union[str, Sequence[str], None] = 'b9a6b29d0915'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Для SQLite — через batch_alter_table
    with op.batch_alter_table("leads", schema=None) as batch:
        batch.add_column(
            sa.Column("message", sa.String(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("leads", schema=None) as batch:
        batch.drop_column("message")
