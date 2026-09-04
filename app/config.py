from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CloudOps"
    app_env: str = "development"
    app_debug: bool = True
    app_version: str = "0.1.0"

    database_url: Optional[str] = None
    secret_key: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()