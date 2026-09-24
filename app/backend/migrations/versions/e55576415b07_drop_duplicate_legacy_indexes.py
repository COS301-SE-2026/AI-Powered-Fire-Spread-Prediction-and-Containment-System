"""drop duplicate legacy indexes

Revision ID: e55576415b07
Revises: 7db2f82cc86f
Create Date: 2026-09-24 12:21:42.734727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e55576415b07'
down_revision: Union[str, None] = '7db2f82cc86f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_fire_reports_photo_hash")
    op.execute("DROP INDEX IF EXISTS idx_fire_reports_submitted_at")


def downgrade() -> None:
    pass
