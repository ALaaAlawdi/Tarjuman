from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    POSTGRESQL_DB_HOST: str = Field(..., env="POSTGRESQL_DB_HOST")
    POSTGRESQL_DB_PORT: int = Field(5432, env="POSTGRESQL_DB_PORT")
    POSTGRESQL_DB_USER: str = Field(..., env="POSTGRESQL_DB_USER")
    POSTGRESQL_DB_PASSWORD: str = Field(..., env="POSTGRESQL_DB_PASSWORD")
    POSTGRESQL_DB_NAME: str = Field(..., env="POSTGRESQL_DB_NAME")
    

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()