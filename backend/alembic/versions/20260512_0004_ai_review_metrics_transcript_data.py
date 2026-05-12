"""Add structured transcripts and AI review metrics.

Revision ID: 20260512_0004
Revises: 20260512_0003
Create Date: 2026-05-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260512_0004"
down_revision: Union[str, None] = "20260512_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EMPTY_JSON_LIST = "[]"


def upgrade() -> None:
    op.add_column(
        "calls",
        sa.Column(
            "transcript_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=EMPTY_JSON_LIST,
        ),
    )
    op.alter_column("calls", "transcript_data", server_default=None)

    op.add_column(
        "ai_reviews",
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=EMPTY_JSON_LIST,
        ),
    )
    op.alter_column("ai_reviews", "metrics", server_default=None)


def downgrade() -> None:
    op.drop_column("ai_reviews", "metrics")
    op.drop_column("calls", "transcript_data")
