"""Add customizable prospect status options.

Revision ID: 20260511_0002
Revises: 20260511_0001
Create Date: 2026-05-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260511_0002"
down_revision: Union[str, None] = "20260511_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_STATUS_OPTIONS = '["New", "Contacted", "Engaged", "Advancing", "Scheduled", "Converted", "Archived"]'


def upgrade() -> None:
    op.add_column(
        "user_settings",
        sa.Column(
            "status_options",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=DEFAULT_STATUS_OPTIONS,
        ),
    )
    op.alter_column("user_settings", "status_options", server_default=None)


def downgrade() -> None:
    op.drop_column("user_settings", "status_options")
