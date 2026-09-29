"""add push_subscription to users

Revision ID: 2bfc68816704
Revises: 0c36daf7a339
Create Date: 2026-09-28 19:23:50.028057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bfc68816704'
down_revision: Union[str, None] = '0c36daf7a339'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("push_subscription", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "push_subscription")
