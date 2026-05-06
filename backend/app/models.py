from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    call_logs: Mapped[list["CallLog"]] = relationship(
        back_populates="contact",
        passive_deletes=True,
    )
    meetings: Mapped[list["Meeting"]] = relationship(
        back_populates="contact",
        passive_deletes=True,
    )


class CallLog(Base):
    __tablename__ = "call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    contact_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(40), nullable=False)
    outcome: Mapped[str] = mapped_column(String(40), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    contact: Mapped[Contact | None] = relationship(back_populates="call_logs")
    meetings: Mapped[list["Meeting"]] = relationship(
        back_populates="call_log",
        passive_deletes=True,
    )


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    call_log_id: Mapped[int | None] = mapped_column(
        ForeignKey("call_logs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    contact_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(40), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    contact: Mapped[Contact | None] = relationship(back_populates="meetings")
    call_log: Mapped[CallLog | None] = relationship(back_populates="meetings")
