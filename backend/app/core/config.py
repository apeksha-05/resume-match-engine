from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Resume Match Engine API"
    environment: str = "development"

    # Filled in during Phase 4B when the database is connected.
    database_url: str = ""

    # Gemini API key for real AI extraction (Phase 5+). Leave blank to use the
    # mock extraction backend instead, no key required.
    gemini_api_key: str = ""

    # Explicitly force mock mode even if a key is present. Useful for offline
    # development or avoiding API usage during routine testing.
    force_mock_llm: bool = False

    # Used by app/core/auth.py to verify JWTs via Supabase's JWKS endpoint.
    supabase_url: str = ""

    # Comma-separated list of allowed frontend origins for CORS.
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def use_mock_llm(self) -> bool:
        """True whenever there's no real API key, or mock mode is explicitly forced."""
        return self.force_mock_llm or not self.gemini_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()