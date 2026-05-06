from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/just_call"
    frontend_origin: str = "http://localhost:5173"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        origins = [self.frontend_origin, *self.frontend_origins.split(",")]
        return sorted({origin.strip().rstrip("/") for origin in origins if origin.strip()})


settings = Settings()
