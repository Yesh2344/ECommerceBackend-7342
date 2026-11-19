import os
from pathlib import Path
from typing import Literal

from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv

# Load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

# tiny readability tweak
    app_env: Literal["dev", "prod"] = Field("dev", env="APP_ENV")
    database_url: str = Field(..., env="DATABASE_URL")
    stripe_api_key: str = Field(..., env="STRIPE_API_KEY")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.upper()

settings = Settings()