import time
from loguru import logger
from typing import Optional
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout

from .config import settings


class ElasticsearchClient:
    _instance: Optional[Elasticsearch] = None

    @classmethod
    def get_instance(cls) -> Elasticsearch:
        """Get or create an Elasticsearch client singleton instance with connection pooling"""
        if cls._instance is None:
            max_retries = 5
            base_delay = 5  # seconds
            retry_count = 0

            while retry_count < max_retries:
                try:
                    logger.info(
                        f"Attempting to connect to Elasticsearch (attempt {retry_count + 1}/{max_retries})..."
                    )
                    cls._instance = Elasticsearch(
                        hosts=[settings.ES_SERVER],
                        basic_auth=(settings.ES_USER, settings.ES_PASSWORD),
                        timeout=settings.ES_TIMEOUT,
                        max_retries=settings.ES_MAX_RETRIES,
                    )

                    # Test connection
                    if not cls._instance.ping():
                        raise ConnectionError("Could not connect to Elasticsearch")

                    logger.info("Successfully connected to Elasticsearch")

                    return cls._instance

                except (ConnectionError, ConnectionTimeout) as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        delay = base_delay * (
                            2 ** (retry_count - 1)
                        )  # exponential backoff
                        logger.warning(f"Failed to connect to Elasticsearch: {str(e)}")
                        logger.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"Failed to connect to Elasticsearch after {max_retries} attempts"
                        )
                        raise
        return cls._instance

    @classmethod
    def health_check(cls) -> bool:
        """Check if Elasticsearch connection is healthy"""
        try:
            client = cls.get_instance()
            return client.ping()
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    @classmethod
    def close(cls) -> None:
        """Close the Elasticsearch connection"""
        if cls._instance is not None:
            try:
                cls._instance.close()
                cls._instance = None
                logger.info("Elasticsearch connection closed")
            except Exception as e:
                logger.error(f"Error closing Elasticsearch connection: {str(e)}")


def get_elasticsearch_client() -> Elasticsearch:
    """Get an Elasticsearch client instance"""
    return ElasticsearchClient.get_instance()
