import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    ENV: str = "development"
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:4200"]
    SUPABASE_JWT_SECRET: str = "your-supabase-jwt-secret-placeholder"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    SUPABASE_URL: str = "https://your-supabase-project.supabase.co"
    SUPABASE_SERVICE_ROLE_KEY: str = "your-supabase-service-role-key-placeholder"
    GEMINI_API_KEY: str = "your-gemini-api-key-placeholder"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def enforce_asyncpg_driver(cls, value: str) -> str:
        if isinstance(value, str):
            if value.startswith("postgres://"):
                return value.replace("postgres://", "postgresql+asyncpg://", 1)
            elif value.startswith("postgresql://"):
                return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            # If empty string, return empty list
            if not value.strip():
                return []
            try:
                # Try parsing as JSON array (e.g. '["http://localhost:4200"]')
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            
            # Fallback to comma-separated list
            return [o.strip() for o in value.split(",") if o.strip()]
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
export_settings = settings # For convenience
