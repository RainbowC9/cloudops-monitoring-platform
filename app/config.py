from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CloudOps"
    app_env: str = "development"
    app_debug: bool = True
    app_version: str = "0.4.0"

    database_url: Optional[str] = None
    secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    prometheus_url: str = "http://127.0.0.1:9090"
    prometheus_timeout_seconds: float = 5.0
    
    windows_exporter_port: int = 9182

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()