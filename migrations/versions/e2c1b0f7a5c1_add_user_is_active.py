"""add is_active to users

Revision ID: e2c1b0f7a5c1
Revises: d4b21dbddcd2
Create Date: 2026-02-11 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e2c1b0f7a5c1'
down_revision: Union[str, Sequence[str], None] = 'd4b21dbddcd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=False))
    op.alter_column('users', 'is_active', server_default=None)


def downgrade() -> None:
    op.drop_column('users', 'is_active')
