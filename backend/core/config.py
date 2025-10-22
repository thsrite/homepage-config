from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

    # App configuration
    app_name: str = "Homepage Configuration Tool"
    app_version: str = "1.0.0"
    debug: bool = True

    # Authentication configuration (required - must be set in environment or .env file)
    auth_username: str = "admin"  # Default username, CHANGE THIS!
    auth_password: str = "admin"  # Default password, CHANGE THIS!
    session_secret: str = "change-this-to-a-random-secret-key"
    session_expire_minutes: int = 60 * 24  # 24 hours

    # File paths
    config_path: str = "config/services.yaml"
    example_config_path: str = "config/example.yaml"
    upload_dir: str = "uploads"

    # API configuration
    api_prefix: str = "/api"

    # Frontend configuration
    frontend_path: str = "frontend"

    # CORS settings
    cors_origins: list = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()