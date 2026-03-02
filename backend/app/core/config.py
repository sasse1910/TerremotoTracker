from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "insecure-default-change-in-production"  # noqa: S105

    DATABASE_URL: str
    REDIS_URL: str
    CACHE_TTL_SECONDS: int = 60
    CACHE_TTL_VOLCANOES: int = 3600

    USGS_BASE_URL: str = "https://earthquake.usgs.gov/fdsnws/event/1"
    USGS_FEED_URL: str = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary"
    GVP_BASE_URL: str = "https://volcano.si.edu/api"

    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list) -> list[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
