from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Resume Match Engine API"
    environment: str = "development"

    # Filled in during Phase 4B when the database is connected.
    database_url: str = ""

    # Filled in during Phase 5 when Claude extraction is added.
    anthropic_api_key: str = ""

    # Filled in during Phase 8 when Supabase Auth is wired up.
    supabase_url: str = ""
    supabase_jwt_secret: str = ""

    # Comma-separated list of allowed frontend origins for CORS.
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()