from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/just_call"
    frontend_origin: str = "http://localhost:5173"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_phone_number: str | None = None
    twilio_api_key_sid: str | None = None
    twilio_api_key_secret: str | None = None
    twilio_twiml_app_sid: str | None = None
    twilio_voice_url: str | None = None
    groq_api_key: str | None = Field(default=None, validation_alias=AliasChoices("GROQ_API_KEY", "API_KEY_GROQ"))
    groq_model: str = "openai/gpt-oss-120b"
    groq_transcription_model: str = "whisper-large-v3"
    seed_on_startup: bool = False

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @property
    def cors_origins(self) -> list[str]:
        origins = [self.frontend_origin, *self.frontend_origins.split(",")]
        return sorted({origin.strip().rstrip("/") for origin in origins if origin.strip()})


settings = Settings()
