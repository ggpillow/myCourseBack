"""initial schema

Revision ID: 6acc2e6f4473
Revises: 83b6be5bd843
Create Date: 2026-05-31 01:40:39.593841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6acc2e6f4473'
down_revision: Union[str, Sequence[str], None] = '83b6be5bd843'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'role',
               existing_type=postgresql.ENUM('user', 'admin', name='user_role'),
               server_default=None,
               existing_nullable=False)
    op.drop_constraint(op.f('users_email_key'), 'users', type_='unique')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_unique_constraint(op.f('users_email_key'), 'users', ['email'], postgresql_nulls_not_distinct=False)
    op.alter_column('users', 'role',
               existing_type=postgresql.ENUM('user', 'admin', name='user_role'),
               server_default=sa.text("'user'::user_role"),
               existing_nullable=False)