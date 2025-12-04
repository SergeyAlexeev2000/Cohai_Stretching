"""add attendances table (fixed)

Revision ID: 2b06bc1fb6c1
Revises: 91ee455cead4
Create Date: 2025-11-28 23:34:02.788121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b06bc1fb6c1'
down_revision: Union[str, Sequence[str], None] = '91ee455cead4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Если таблица уже есть — дропаем её
    if "attendances" in inspector.get_table_names():
        op.drop_table("attendances")

    # И создаём НОРМАЛЬНУЮ версию
    op.create_table(
        "attendances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "class_session_id",
            sa.Integer(),
            sa.ForeignKey("class_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "membership_id",
            sa.Integer(),
            sa.ForeignKey("memberships.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "class_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="PLANNED",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "user_id",
            "class_session_id",
            "class_date",
            name="uq_attendance_user_session_date",
        ),
    )


def downgrade() -> None:
    op.drop_table("attendances")
