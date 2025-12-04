"""add attendances table

Revision ID: 91ee455cead4
Revises: 76d7baddc94f
Create Date: 2025-11-28 21:25:57.454335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91ee455cead4'
down_revision: Union[str, Sequence[str], None] = '76d7baddc94f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
        sa.Column(
            "class_date",
            sa.Date(),
            nullable=False,
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