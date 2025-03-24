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


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = config.get("LOG_LEVEL", default="INFO")
    LOG_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    LOG_FILE: str = config.get("LOG_FILE", default="logs/error.log")
    LOG_ROTATION: str = config.get("LOG_ROTATION", default="500 MB")
    LOG_RETENTION: str = config.get("LOG_RETENTION", default="10 days")


class ElasticsearchSettings(BaseSettings):
    ES_SERVER: str = config.get("ES_SERVER")
    ES_USER: str = config.get("ES_USER")
    ES_PASSWORD: str = config.get("ES_PASSWORD")
    ES_TIMEOUT: int = config.get("ES_TIMEOUT", default=30)
    ES_MAX_RETRIES: int = config.get("ES_MAX_RETRIES", default=3)
    ES_POOL_SIZE: int = config.get("ES_POOL_SIZE", default=10)

    ES_LOG_INDEX_NAME: str = "search_query_logs"
    ES_LOG_INDEX_MAPPINGS: dict = {
        "properties": {
            "ip": {"type": "keyword"},
            "username": {"type": "keyword"},
            "query": {"type": "text"},
            "timestamp": {"type": "date"},
        }
    }


class RabbitMQSettings(BaseSettings):
    RABBITMQ_HOST: str = config.get("RABBITMQ_HOST", default="rabbitmq")
    RABBITMQ_PORT: int = config.get("RABBITMQ_PORT", default=5672)
    RABBITMQ_USER: str = config.get("RABBITMQ_USER", default="guest")
    RABBITMQ_PASSWORD: str = config.get("RABBITMQ_PASSWORD", default="guest")
    RABBITMQ_VHOST: str = config.get("RABBITMQ_VHOST", default="/")
    RABBITMQ_QUEUE_NAME: str = "search_query_queue"
    RABBITMQ_HEARTBEAT: int = config.get("RABBITMQ_HEARTBEAT", default=600)
    RABBITMQ_BLOCKED_CONNECTION_TIMEOUT: int = config.get(
        "RABBITMQ_BLOCKED_CONNECTION_TIMEOUT", default=300
    )


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")


class Settings(
    AppSettings,
    LoggingSettings,
    EnvironmentSettings,
    ElasticsearchSettings,
    RabbitMQSettings,
):
    pass


settings = Settings()
