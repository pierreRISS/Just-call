from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Priority = Literal["High", "Medium", "Low"]
Temperature = Literal["Warm", "Neutral", "Cold"]
CallStatus = Literal["planned", "in_progress", "completed", "failed"]


class UserRead(BaseModel):
    id: int
    email: str
    display_name: str
    role: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str = Field(..., max_length=255)
    display_name: str = Field(..., max_length=120)
    role: str | None = Field(default=None, max_length=120)

    @field_validator("email", "display_name", "role", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        stripped = value.strip()
        return stripped or None


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1, max_length=255)

    @field_validator("email", mode="before")
    @classmethod
    def strip_email(cls, value: str) -> str:
        return value.strip().lower()


class AuthSessionRead(BaseModel):
    token: str
    user: UserRead


class ProspectBase(BaseModel):
    name: str = Field(..., max_length=120)
    company: str = Field(..., max_length=120)
    role: str | None = Field(default=None, max_length=120)
    phone_number: str = Field(..., min_length=3, max_length=40)
    email: str | None = Field(default=None, max_length=255)
    status: str = Field(default="New", max_length=40)
    priority: Priority = "Medium"
    temperature: Temperature = "Neutral"
    context: str | None = Field(default=None, max_length=4000)
    previous_notes: str | None = Field(default=None, max_length=4000)
    call_objective: str | None = Field(default=None, max_length=2000)
    possible_objections: list[str] = Field(default_factory=list)
    priority_signals: list[str] = Field(default_factory=list)
    last_touch: str | None = Field(default=None, max_length=255)
    last_call: str | None = Field(default=None, max_length=120)

    @field_validator(
        "name",
        "company",
        "role",
        "phone_number",
        "email",
        "context",
        "previous_notes",
        "call_objective",
        "last_touch",
        "last_call",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        stripped = value.strip()
        return stripped or None

    @field_validator("possible_objections", "priority_signals")
    @classmethod
    def clean_string_list(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value.strip()]


class ProspectCreate(ProspectBase):
    pass


class ProspectUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    company: str | None = Field(default=None, max_length=120)
    role: str | None = Field(default=None, max_length=120)
    phone_number: str | None = Field(default=None, min_length=3, max_length=40)
    email: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=40)
    priority: Priority | None = None
    temperature: Temperature | None = None
    context: str | None = Field(default=None, max_length=4000)
    previous_notes: str | None = Field(default=None, max_length=4000)
    call_objective: str | None = Field(default=None, max_length=2000)
    possible_objections: list[str] | None = None
    priority_signals: list[str] | None = None
    last_touch: str | None = Field(default=None, max_length=255)
    last_call: str | None = Field(default=None, max_length=120)

    @field_validator(
        "name",
        "company",
        "role",
        "phone_number",
        "email",
        "context",
        "previous_notes",
        "call_objective",
        "last_touch",
        "last_call",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        stripped = value.strip()
        return stripped or None


class ProspectRead(ProspectBase):
    id: int
    user_id: int
    last_called_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIReviewBase(BaseModel):
    global_score: int = Field(..., ge=0, le=100)
    summary: str = Field(..., max_length=5000)
    strengths: list[str] = Field(default_factory=list)
    improvement_focus: str = Field(..., max_length=3000)


class AIReviewCreate(AIReviewBase):
    call_id: int


class AIReviewUpdate(BaseModel):
    global_score: int | None = Field(default=None, ge=0, le=100)
    summary: str | None = Field(default=None, max_length=5000)
    strengths: list[str] | None = None
    improvement_focus: str | None = Field(default=None, max_length=3000)


class AIReviewRead(AIReviewBase):
    id: int
    user_id: int
    call_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CallBase(BaseModel):
    prospect_id: int | None = None
    prospect_name: str | None = Field(default=None, max_length=120)
    company: str | None = Field(default=None, max_length=120)
    phone_number: str | None = Field(default=None, min_length=3, max_length=40)
    status: CallStatus = "completed"
    quick_action: str | None = Field(default=None, max_length=80)
    duration_seconds: int = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=8000)
    transcript: str | None = Field(default=None, max_length=50000)
    ai_summary: str | None = Field(default=None, max_length=5000)
    global_score: int | None = Field(default=None, ge=0, le=100)
    tags: list[str] = Field(default_factory=list)
    twilio_sid: str | None = Field(default=None, max_length=80)
    recording_url: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None

    @field_validator("prospect_name", "company", "phone_number", "quick_action", "notes", "transcript", "ai_summary", "twilio_sid", "recording_url", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        stripped = value.strip()
        return stripped or None


class CallCreate(CallBase):
    pass


class CallUpdate(BaseModel):
    status: CallStatus | None = None
    quick_action: str | None = Field(default=None, max_length=80)
    duration_seconds: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=8000)
    transcript: str | None = Field(default=None, max_length=50000)
    ai_summary: str | None = Field(default=None, max_length=5000)
    global_score: int | None = Field(default=None, ge=0, le=100)
    tags: list[str] | None = None
    twilio_sid: str | None = Field(default=None, max_length=80)
    recording_url: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None


class CallRead(CallBase):
    id: int
    user_id: int
    prospect_id: int | None
    prospect_name: str
    company: str | None
    phone_number: str
    created_at: datetime
    ai_review: AIReviewRead | None = None

    model_config = ConfigDict(from_attributes=True)


class ReplayMessage(BaseModel):
    speaker: Literal["ai", "seller"]
    text: str = Field(..., max_length=4000)


class ReplaySessionBase(BaseModel):
    call_id: int | None = None
    prospect_id: int | None = None
    difficulty: str = Field(default="Balanced", max_length=40)
    objection_type: str = Field(default="Tool fatigue", max_length=80)
    prospect_behavior: str = Field(default="Skeptical but fair", max_length=80)
    simulation_mode: str = Field(default="Objection practice", max_length=80)
    status: str = Field(default="ready", max_length=40)
    messages: list[ReplayMessage] = Field(default_factory=list)


class ReplaySessionCreate(ReplaySessionBase):
    pass


class ReplaySessionUpdate(BaseModel):
    difficulty: str | None = Field(default=None, max_length=40)
    objection_type: str | None = Field(default=None, max_length=80)
    prospect_behavior: str | None = Field(default=None, max_length=80)
    simulation_mode: str | None = Field(default=None, max_length=80)
    status: str | None = Field(default=None, max_length=40)
    messages: list[ReplayMessage] | None = None


class ReplaySessionRead(ReplaySessionBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSettingsBase(BaseModel):
    audio_input: str = Field(default="Studio microphone", max_length=120)
    noise_cleanup: str = Field(default="Soft", max_length=40)
    microphone_permission: str = Field(default="granted", max_length=40)
    notifications: dict[str, bool] = Field(default_factory=dict)
    ai_preferences: dict[str, str] = Field(default_factory=dict)
    integrations: dict[str, str] = Field(default_factory=dict)
    status_options: list[str] = Field(default_factory=list)


class UserSettingsUpdate(BaseModel):
    audio_input: str | None = Field(default=None, max_length=120)
    noise_cleanup: str | None = Field(default=None, max_length=40)
    microphone_permission: str | None = Field(default=None, max_length=40)
    notifications: dict[str, bool] | None = None
    ai_preferences: dict[str, str] | None = None
    integrations: dict[str, str] | None = None
    status_options: list[str] | None = None


class UserSettingsRead(UserSettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OutboundCallCreate(BaseModel):
    to: str = Field(..., min_length=3, max_length=40)
    prospect_id: int | None = None

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
