import os

import yaml
from pydantic import BaseModel


class AppConfig(BaseModel):
    name: str
    version: str


class ScraperConfig(BaseModel):
    headless: bool
    implicitly_wait: int
    page_load_timeout: int
    retry_attempts: int
    max_pages_default: int
    max_reviews_default: int


class StorageConfig(BaseModel):
    default_export_format: str
    export_dir: str
    sqlite_db_path: str


class LoggingConfig(BaseModel):
    level: str


class Settings(BaseModel):
    app: AppConfig
    scraper: ScraperConfig
    storage: StorageConfig
    logging: LoggingConfig


def load_settings(config_path: str = "config/settings.yaml") -> Settings:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return Settings(**data)


# Global settings instance
try:
    settings = load_settings()
except Exception:
    settings = None
