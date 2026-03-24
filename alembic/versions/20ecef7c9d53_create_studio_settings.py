"""create studio settings

Revision ID: 20ecef7c9d53
Revises: 5b2a7884f027
Create Date: 2025-12-24 15:43:45.358873

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20ecef7c9d53'
down_revision: Union[str, Sequence[str], None] = '5b2a7884f027'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "studio_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("studio_capacity", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("reservation_ttl_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("offer_ttl_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    # вставим дефолтную строку id=1
    op.execute("INSERT INTO studio_settings (id) VALUES (1)")


def downgrade() -> None:
    op.drop_table("studio_settings")
