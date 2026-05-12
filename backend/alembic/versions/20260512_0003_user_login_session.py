"""Add user login session fields.

Revision ID: 20260512_0003
Revises: 20260511_0002
Create Date: 2026-05-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260512_0003"
down_revision: Union[str, None] = "20260511_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("session_token", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_users_session_token"), "users", ["session_token"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_session_token"), table_name="users")
    op.drop_column("users", "session_token")
    op.drop_column("users", "password_hash")
