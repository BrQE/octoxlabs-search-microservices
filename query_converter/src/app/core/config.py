import os
from enum import Enum

from pydantic_settings import BaseSettings
from starlette.config import Config

current_file_dir = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(current_file_dir, "..", "..", ".env")
config = Config(env_path)


class AppSettings(BaseSettings):
    APP_NAME: str = config.get("APP_NAME", default="Query Converter API")
    APP_DESCRIPTION: str | None = config.get("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config.get("APP_VERSION", default=None)
    LICENSE_NAME: str | None = config("LICENSE", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)
    
    # Logging settings
    LOG_LEVEL: str = config.get("LOG_LEVEL", default="INFO")
    LOG_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    LOG_FILE: str = config.get("LOG_FILE", default="logs/error.log")
    LOG_ROTATION: str = config.get("LOG_ROTATION", default="500 MB")
    LOG_RETENTION: str = config.get("LOG_RETENTION", default="10 days")


class TestSettings(BaseSettings):
    ...


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")


class Settings(
    AppSettings,
    TestSettings,
    EnvironmentSettings,
):
    pass


settings = Settings()