from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""

    # App configuration
    app_name: str = "Homepage Configuration Tool"
    app_version: str = "1.0.0"
    debug: bool = True

    # File paths
    config_path: str = "configs/services.yaml"
    example_config_path: str = "configs/example.yaml"
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