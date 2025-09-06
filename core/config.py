from pathlib import Path
import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent  # Tarjuman/

class Settings(BaseSettings):
    # DB
    POSTGRESQL_DB_HOST: str = Field(..., env="POSTGRESQL_DB_HOST")
    POSTGRESQL_DB_PORT: int = Field(5432, env="POSTGRESQL_DB_PORT")
    POSTGRESQL_DB_USER: str = Field(..., env="POSTGRESQL_DB_USER")
    POSTGRESQL_DB_PASSWORD: str = Field(..., env="POSTGRESQL_DB_PASSWORD")
    POSTGRESQL_DB_NAME: str = Field(..., env="POSTGRESQL_DB_NAME")
    # api 
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")

    # App
    AGENT_VERSION_ROUTER_API: str = Field("/v1", env="AGENT_VERSION_ROUTER_API")
    APP_DEBUG: bool = Field(False, env="APP_DEBUG")  # <-- add this
    
    # Security settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRY_DAYS: int = Field(120, env="ACCESS_TOKEN_EXPIRY_DAYS")


    # Paths
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MEDIA_DIR: Path = BASE_DIR / "media" / "images"
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
os.makedirs(settings.MEDIA_DIR, exist_ok=True) 