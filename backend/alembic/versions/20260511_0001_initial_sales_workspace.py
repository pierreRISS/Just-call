"""Initial sales workspace schema.

Revision ID: 20260511_0001
Revises:
Create Date: 2026-05-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260511_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "prospects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("company", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=True),
        sa.Column("phone_number", sa.String(length=40), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("temperature", sa.String(length=20), nullable=False),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("previous_notes", sa.Text(), nullable=True),
        sa.Column("call_objective", sa.Text(), nullable=True),
        sa.Column("possible_objections", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("priority_signals", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("last_touch", sa.String(length=255), nullable=True),
        sa.Column("last_call", sa.String(length=120), nullable=True),
        sa.Column("last_called_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "phone_number", name="uq_prospects_user_phone"),
    )
    op.create_index(op.f("ix_prospects_id"), "prospects", ["id"], unique=False)
    op.create_index(op.f("ix_prospects_phone_number"), "prospects", ["phone_number"], unique=False)
    op.create_index(op.f("ix_prospects_user_id"), "prospects", ["user_id"], unique=False)

    op.create_table(
        "calls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("prospect_id", sa.Integer(), nullable=True),
        sa.Column("prospect_name", sa.String(length=120), nullable=False),
        sa.Column("company", sa.String(length=120), nullable=True),
        sa.Column("phone_number", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("quick_action", sa.String(length=80), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("global_score", sa.Integer(), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("twilio_sid", sa.String(length=80), nullable=True),
        sa.Column("recording_url", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["prospect_id"], ["prospects.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_calls_id"), "calls", ["id"], unique=False)
    op.create_index(op.f("ix_calls_prospect_id"), "calls", ["prospect_id"], unique=False)
    op.create_index(op.f("ix_calls_twilio_sid"), "calls", ["twilio_sid"], unique=False)
    op.create_index(op.f("ix_calls_user_id"), "calls", ["user_id"], unique=False)

    op.create_table(
        "ai_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("call_id", sa.Integer(), nullable=False),
        sa.Column("global_score", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("strengths", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("improvement_focus", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["call_id"], ["calls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("call_id"),
    )
    op.create_index(op.f("ix_ai_reviews_call_id"), "ai_reviews", ["call_id"], unique=True)
    op.create_index(op.f("ix_ai_reviews_id"), "ai_reviews", ["id"], unique=False)
    op.create_index(op.f("ix_ai_reviews_user_id"), "ai_reviews", ["user_id"], unique=False)

    op.create_table(
        "replay_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("call_id", sa.Integer(), nullable=True),
        sa.Column("prospect_id", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=40), nullable=False),
        sa.Column("objection_type", sa.String(length=80), nullable=False),
        sa.Column("prospect_behavior", sa.String(length=80), nullable=False),
        sa.Column("simulation_mode", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("messages", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["call_id"], ["calls.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["prospect_id"], ["prospects.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_replay_sessions_call_id"), "replay_sessions", ["call_id"], unique=False)
    op.create_index(op.f("ix_replay_sessions_id"), "replay_sessions", ["id"], unique=False)
    op.create_index(op.f("ix_replay_sessions_prospect_id"), "replay_sessions", ["prospect_id"], unique=False)
    op.create_index(op.f("ix_replay_sessions_user_id"), "replay_sessions", ["user_id"], unique=False)

    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("audio_input", sa.String(length=120), nullable=False),
        sa.Column("noise_cleanup", sa.String(length=40), nullable=False),
        sa.Column("microphone_permission", sa.String(length=40), nullable=False),
        sa.Column("notifications", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("ai_preferences", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("integrations", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_settings_id"), "user_settings", ["id"], unique=False)
    op.create_index(op.f("ix_user_settings_user_id"), "user_settings", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_settings_user_id"), table_name="user_settings")
    op.drop_index(op.f("ix_user_settings_id"), table_name="user_settings")
    op.drop_table("user_settings")
    op.drop_index(op.f("ix_replay_sessions_user_id"), table_name="replay_sessions")
    op.drop_index(op.f("ix_replay_sessions_prospect_id"), table_name="replay_sessions")
    op.drop_index(op.f("ix_replay_sessions_id"), table_name="replay_sessions")
    op.drop_index(op.f("ix_replay_sessions_call_id"), table_name="replay_sessions")
    op.drop_table("replay_sessions")
    op.drop_index(op.f("ix_ai_reviews_user_id"), table_name="ai_reviews")
    op.drop_index(op.f("ix_ai_reviews_id"), table_name="ai_reviews")
    op.drop_index(op.f("ix_ai_reviews_call_id"), table_name="ai_reviews")
    op.drop_table("ai_reviews")
    op.drop_index(op.f("ix_calls_user_id"), table_name="calls")
    op.drop_index(op.f("ix_calls_twilio_sid"), table_name="calls")
    op.drop_index(op.f("ix_calls_prospect_id"), table_name="calls")
    op.drop_index(op.f("ix_calls_id"), table_name="calls")
    op.drop_table("calls")
    op.drop_index(op.f("ix_prospects_user_id"), table_name="prospects")
    op.drop_index(op.f("ix_prospects_phone_number"), table_name="prospects")
    op.drop_index(op.f("ix_prospects_id"), table_name="prospects")
    op.drop_table("prospects")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
