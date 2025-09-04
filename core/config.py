from pathlib import Path
import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent  # Tarjuman/

class Settings(BaseSettings):
    # DB
    POSTGRESQL_DB_HOST: str = Field(..., env="POSTGRESQL_DB_HOST")
    POSTGRESQL_DB_PORT: int = Field(5432, env="POSTGRESQL_DB_PORT")
    POSTGRESQL_DB_USER: str = Field(..., env="POSTGRESQL_DB_USER")
    POSTGRESQL_DB_PASSWORD: str = Field(..., env="POSTGRESQL_DB_PASSWORD")
    POSTGRESQL_DB_NAME: str = Field(..., env="POSTGRESQL_DB_NAME")

    # App
    AGENT_VERSION_ROUTER_API: str = Field("/v1", env="AGENT_VERSION_ROUTER_API")
    APP_DEBUG: bool = Field(False, env="APP_DEBUG")  # <-- add this

    # Paths
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    LOG_DIR: Path = BASE_DIR / "logs"

    # Pydantic v2 settings
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        case_sensitive=True,
        # optional: ignore any extra keys in .env instead of erroring
        # extra="ignore",
    )

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)
