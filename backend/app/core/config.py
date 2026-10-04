from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AALA PRESSWAALA API"
    app_version: str = "1.18.0"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    debug: bool = False
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    database_url: str = Field(default="", description="PostgreSQL connection URL")
    supabase_url: str = ""
    supabase_service_key: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "ap-south-1"
    firebase_project_id: str = ""
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    google_maps_api_key: str = ""
    jwt_secret: str = "CHANGE_ME_IN_ENV"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    delivery_code_ttl_minutes: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
