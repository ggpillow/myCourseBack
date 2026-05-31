"""add user role

Revision ID: f1504cf28880
Revises: 3ce8cf079bf2
Create Date: 2026-05-30 15:13:56.619701

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f1504cf28880'
down_revision: Union[str, Sequence[str], None] = '3ce8cf079bf2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_role = sa.Enum("user", "admin", name="user_role")
    user_role.create(op.get_bind())

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role,
            nullable=False,
            server_default="user",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "role")
    sa.Enum(name="user_role").drop(op.get_bind())