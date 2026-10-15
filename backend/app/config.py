from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./reviewforge.db"
    redis_url: str = "redis://localhost:6379/0"
    github_webhook_secret: str = "replace-me"
    github_token: str = ""
    reviewforge_eager: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

