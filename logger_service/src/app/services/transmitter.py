import json
from datetime import datetime
from loguru import logger

from ..core.config import settings
from ..core.database import get_elasticsearch_client


class Transmitter:
    def __init__(self):
        logger.info("Initializing Transmitter service")
        self.es = get_elasticsearch_client()
        logger.info("Elasticsearch client initialized successfully")
        
    def send_to_elasticsearch(self, ch, method, properties, body):
        """Process incoming log messages"""
        try:
            # Parse message
            logger.debug(f"Received message: {body}")
            message = json.loads(body)
            logger.info(f"Processing message - Query: {message['query']}, User: {message['username']}, IP: {message['ip']}")
            
            # Store in Elasticsearch
            document = {
                "ip": message['ip'],
                "username": message['username'],
                "query": message['query'],
                "timestamp": datetime.now().isoformat()
            }
            logger.debug(f"Preparing to index document: {document}")
            
            response = self.es.index(
                index=settings.ES_LOG_INDEX_NAME,
                body=document
            )
            logger.info(f"Successfully indexed document with ID: {response['_id']}")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug(f"Acknowledged message with delivery tag: {method.delivery_tag}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message as JSON: {str(e)}")
            logger.error(f"Raw message: {body}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            logger.exception(f"Error processing message: {str(e)}")
            logger.error(f"Message that caused error: {body}")
            # Negative acknowledgment to requeue the message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
