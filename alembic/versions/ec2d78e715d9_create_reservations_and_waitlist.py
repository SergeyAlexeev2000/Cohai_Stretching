"""create reservations and waitlist

Revision ID: ec2d78e715d9
Revises: 20ecef7c9d53
Create Date: 2025-12-24 15:46:45.681602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec2d78e715d9'
down_revision: Union[str, Sequence[str], None] = '20ecef7c9d53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
