from elasticsearch import Elasticsearch
from .config import ElasticsearchSettings


def get_elasticsearch_client():
    """Get an Elasticsearch client"""
    settings = ElasticsearchSettings()
    es_client = Elasticsearch(settings.SERVER, basic_auth=(settings.USER, settings.PASSWORD))

    try:
        yield es_client
    finally:
        es_client.close()