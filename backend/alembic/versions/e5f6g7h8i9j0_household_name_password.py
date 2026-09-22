"""replace household token with name + password

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-09-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h8i9j0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing households keep their old code as the name, with an empty password
    op.drop_index('ix_households_token', table_name='households')
    with op.batch_alter_table('households') as batch_op:
        batch_op.alter_column('token', new_column_name='name')
        batch_op.add_column(sa.Column('password_hash', sa.String(), nullable=False, server_default=''))
    op.create_index('ix_households_name', 'households', ['name'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_households_name', table_name='households')
    with op.batch_alter_table('households') as batch_op:
        batch_op.drop_column('password_hash')
        batch_op.alter_column('name', new_column_name='token')
    op.create_index('ix_households_token', 'households', ['token'], unique=True)
