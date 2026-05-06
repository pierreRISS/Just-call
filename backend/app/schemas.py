from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContactCreate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    phone_number: str = Field(..., min_length=3, max_length=40)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("name", "phone_number", "notes", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        return stripped or None


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    phone_number: str | None = Field(default=None, min_length=3, max_length=40)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("name", "phone_number", "notes", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        return stripped or None


class ContactRead(BaseModel):
    id: int
    name: str | None
    phone_number: str
    notes: str | None
    created_at: datetime
    last_called_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class CallLogCreate(BaseModel):
    contact_id: int
    outcome: Literal["answered", "no_answer", "voicemail", "failed"]
    duration_seconds: int = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("notes", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        return stripped or None


class CallLogRead(BaseModel):
    id: int
    contact_id: int | None
    contact_name: str | None
    phone_number: str
    outcome: str
    duration_seconds: int
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OutboundCallCreate(BaseModel):
    to: str = Field(..., min_length=3, max_length=40)

    @field_validator("to", mode="before")
    @classmethod
    def strip_to(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        return stripped or None


class OutboundCallRead(BaseModel):
    sid: str
    status: str | None
    to: str
    from_number: str


class VoiceTokenRead(BaseModel):
    token: str
    identity: str


class VoiceConfigRead(BaseModel):
    is_ready: bool
    missing: list[str]
    phone_number: str | None


class MeetingCreate(BaseModel):
    contact_id: int
    call_log_id: int | None = None
    scheduled_at: datetime
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("notes", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        stripped = value.strip()
        return stripped or None


class MeetingRead(BaseModel):
    id: int
    contact_id: int | None
    call_log_id: int | None
    contact_name: str | None
    phone_number: str
    scheduled_at: datetime
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
