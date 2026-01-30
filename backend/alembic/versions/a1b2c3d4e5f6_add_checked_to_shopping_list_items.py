"""add checked to shopping_list_items

Revision ID: a1b2c3d4e5f6
Revises: 91105d06de6e
Create Date: 2026-01-30 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '91105d06de6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('shopping_list_items', sa.Column('checked', sa.Boolean(), nullable=True, server_default=sa.text('0')))


def downgrade() -> None:
    op.drop_column('shopping_list_items', 'checked')
