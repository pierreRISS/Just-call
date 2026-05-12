from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    session_token: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    prospects: Mapped[list["Prospect"]] = relationship(back_populates="user", passive_deletes=True)
    calls: Mapped[list["SalesCall"]] = relationship(back_populates="user", passive_deletes=True)
    ai_reviews: Mapped[list["AIReview"]] = relationship(back_populates="user", passive_deletes=True)
    replay_sessions: Mapped[list["ReplaySession"]] = relationship(back_populates="user", passive_deletes=True)
    settings: Mapped["UserSettings | None"] = relationship(back_populates="user", passive_deletes=True)


class Prospect(Base):
    __tablename__ = "prospects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    company: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="New")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="Medium")
    temperature: Mapped[str] = mapped_column(String(20), nullable=False, default="Neutral")
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    call_objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    possible_objections: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    priority_signals: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    last_touch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_call: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="prospects")
    calls: Mapped[list["SalesCall"]] = relationship(back_populates="prospect", passive_deletes=True)
    replay_sessions: Mapped[list["ReplaySession"]] = relationship(back_populates="prospect", passive_deletes=True)

    __table_args__ = (UniqueConstraint("user_id", "phone_number", name="uq_prospects_user_phone"),)


class SalesCall(Base):
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    prospect_id: Mapped[int | None] = mapped_column(
        ForeignKey("prospects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    prospect_name: Mapped[str] = mapped_column(String(120), nullable=False)
    company: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="completed")
    quick_action: Mapped[str | None] = mapped_column(String(80), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    global_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    twilio_sid: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    recording_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="calls")
    prospect: Mapped[Prospect | None] = relationship(back_populates="calls")
    ai_review: Mapped["AIReview | None"] = relationship(back_populates="call", passive_deletes=True)
    replay_sessions: Mapped[list["ReplaySession"]] = relationship(back_populates="call", passive_deletes=True)


class AIReview(Base):
    __tablename__ = "ai_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    call_id: Mapped[int] = mapped_column(
        ForeignKey("calls.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    global_score: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    strengths: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    improvement_focus: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="ai_reviews")
    call: Mapped[SalesCall] = relationship(back_populates="ai_review")


class ReplaySession(Base):
    __tablename__ = "replay_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    call_id: Mapped[int | None] = mapped_column(ForeignKey("calls.id", ondelete="SET NULL"), nullable=True, index=True)
    prospect_id: Mapped[int | None] = mapped_column(
        ForeignKey("prospects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    difficulty: Mapped[str] = mapped_column(String(40), nullable=False, default="Balanced")
    objection_type: Mapped[str] = mapped_column(String(80), nullable=False, default="Tool fatigue")
    prospect_behavior: Mapped[str] = mapped_column(String(80), nullable=False, default="Skeptical but fair")
    simulation_mode: Mapped[str] = mapped_column(String(80), nullable=False, default="Objection practice")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="ready")
    messages: Mapped[list[dict[str, str]]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="replay_sessions")
    call: Mapped[SalesCall | None] = relationship(back_populates="replay_sessions")
    prospect: Mapped[Prospect | None] = relationship(back_populates="replay_sessions")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    audio_input: Mapped[str] = mapped_column(String(120), nullable=False, default="Studio microphone")
    noise_cleanup: Mapped[str] = mapped_column(String(40), nullable=False, default="Soft")
    microphone_permission: Mapped[str] = mapped_column(String(40), nullable=False, default="granted")
    notifications: Mapped[dict[str, bool]] = mapped_column(JSONB, nullable=False, default=dict)
    ai_preferences: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False, default=dict)
    integrations: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False, default=dict)
    status_options: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="settings")
