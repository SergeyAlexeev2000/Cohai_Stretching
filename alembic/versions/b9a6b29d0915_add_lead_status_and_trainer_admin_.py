"""Add lead status and trainer/admin assignment

Revision ID: b9a6b29d0915
Revises: 5151f9ecbb5e
Create Date: 2025-12-01 00:13:14.404389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9a6b29d0915'
down_revision: Union[str, Sequence[str], None] = '5151f9ecbb5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("leads") as batch:
        batch.add_column(sa.Column(
            "status",
            sa.Enum("NEW", "IN_PROGRESS", "CLOSED", "DECLINED",
                    name="leadstatus"),
            nullable=False,
            server_default="NEW",
        ))
        batch.add_column(sa.Column("assigned_trainer_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("assigned_admin_id", sa.Integer(), nullable=True))

        batch.create_foreign_key(
            "fk_leads_assigned_trainer",
            "trainers",
            ["assigned_trainer_id"],
            ["id"],
        )
        batch.create_foreign_key(
            "fk_leads_assigned_admin",
            "users",
            ["assigned_admin_id"],
            ["id"],
        )


def downgrade() -> None:
    # Обратные действия — тоже batch_mode
    with op.batch_alter_table("leads", schema=None) as batch_op:

        # Удаляем FOREIGN KEY сначала
        batch_op.drop_constraint(
            "fk_leads_assigned_trainer",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "fk_leads_assigned_admin",
            type_="foreignkey",
        )

        # Затем удаляем столбцы
        batch_op.drop_column("assigned_trainer_id")
        batch_op.drop_column("assigned_admin_id")

        # Затем удаляем статус
        batch_op.drop_column("status")

        # И наконец удаляем enum type (только если не нужен)
        # SQLite позволяет просто ignore, но для других БД:
        # op.execute("DROP TYPE IF EXISTS leadstatus")

