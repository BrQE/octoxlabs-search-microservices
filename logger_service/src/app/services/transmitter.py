import json
from datetime import datetime

from ..core.config import settings
from ..core.database import get_elasticsearch_client
from ..core.logger import logging

logger = logging.getLogger(__name__)


class Transmitter:
    def __init__(self):
        self.es = get_elasticsearch_client()
        
    def send_to_elasticsearch(self, ch, method, properties, body):
        """Process incoming log messages"""
        try:
            # Parse message
            message = json.loads(body)
            
            # Log to file
            logger.info(f"Query: {message['query']} - User: {message['username']}")
            
            # Store in Elasticsearch
            self.es.index(
                index=settings.ES_LOG_INDEX_NAME,
                body={
                    "ip": message['ip'],
                    "username": message['username'],
                    "query": message['query'],
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Negative acknowledgment to requeue the message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
