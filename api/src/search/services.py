import requests
from django.conf import settings
from elasticsearch import Elasticsearch
from functools import lru_cache
import logging
import json

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, elasticsearch_client=None):
        self.es_client = elasticsearch_client or Elasticsearch(settings.ELASTICSEARCH_HOST)

    def search(self, query):
        """Main search method combining conversion and execution"""
        es_query = self.convert_query(query)
        logger.info(f"Elasticsearch query: {es_query}")
        # Convert dict to string for caching
        es_query_str = json.dumps(es_query, sort_keys=True)
        return self.execute_search(es_query_str)

    def convert_query(self, query):
        """Convert search query using converter service"""
        try:
            response = requests.post(
                settings.QUERY_CONVERTER_SERVICE_URL,
                json={'query': query}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Query conversion failed: {str(e)}", exc_info=True)
            raise

    @lru_cache(maxsize=1000)
    def execute_search(self, es_query_str):
        """Execute search query on Elasticsearch"""
        try:
            es_query = json.loads(es_query_str)
            response = self.es_client.search(
                index=settings.ELASTICSEARCH_INDEX,
                body=es_query
            )
            return [hit['_source'] for hit in response['hits']['hits']]
        except Exception as e:
            logger.error(f"Elasticsearch search failed: {str(e)}", exc_info=True)
            raise