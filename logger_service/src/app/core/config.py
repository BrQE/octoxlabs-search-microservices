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


class ElasticsearchSettings(BaseSettings):
    SERVER: str = config.get("ELASTICSEARCH_SERVER", default="http://localhost:9200")
    USER: str = config.get("ELASTICSEARCH_USER", default="elastic")
    PASSWORD: str = config.get("ELASTICSEARCH_PASSWORD", default="elastic")

    LOG_INDEX_NAME: str = "search_query_logs"
    LOG_INDEX_MAPPINGS: dict = {
        "properties": {
            "ip": {"type": "keyword"},
            "username": {"type": "keyword"},
            "query": {"type": "text"},
            "timestamp": {"type": "date"}
        }
    }


class RabbitMQSettings(BaseSettings):
    HOST: str = config.get("RABBITMQ_HOST", default="localhost")
    QUEUE_NAME: str = config.get("RABBITMQ_QUEUE_NAME", default="search_query_queue")


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
    ElasticsearchSettings,
    RabbitMQSettings
):
    pass


settings = Settings()