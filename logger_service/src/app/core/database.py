from elasticsearch import Elasticsearch
from .config import settings
from loguru import logger


def get_elasticsearch_client():
    """Get an Elasticsearch client""" 
    try:
        client = Elasticsearch(
            hosts=[settings.ES_SERVER],
            basic_auth=(settings.ES_USER, settings.ES_PASSWORD)
        )
        
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch client: {str(e)}")
        raise