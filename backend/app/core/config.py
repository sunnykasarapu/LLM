from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import dotenv_values

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "sqlite:///./safety_eval.db"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    secret_key: str = Field(default="local-development-only")
    groq_api_key: str = ""
    huggingface_api_key: str = ""
    default_provider: str = "mock"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
    )

    @model_validator(mode="after")
    def load_root_provider_keys(self) -> "Settings":
        root_env = PROJECT_DIR / ".env"
        if not root_env.exists():
            return self
        values = dotenv_values(root_env)
        if not self.groq_api_key:
            self.groq_api_key = values.get("GROQ_API_KEY") or ""
        if not self.huggingface_api_key:
            self.huggingface_api_key = values.get("HUGGINGFACE_API_KEY") or ""
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

