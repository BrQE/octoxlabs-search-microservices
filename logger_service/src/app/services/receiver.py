import pika
import time

from ..core.config import RabbitMQSettings
from ..core.logger import logging
from .transmitter import Transmitter

logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.transmitter = Transmitter()

    def start(self):
        try:
            self.connection = self.create_connection()
            if self.connection is None:
                logger.error("Failed to connect to RabbitMQ")
                raise Exception("Failed to connect to RabbitMQ")
        
            self.channel = self.create_channel()
            if self.channel is None:
                logger.error("Failed to create channel")
                raise Exception("Failed to create channel")
            
            self.channel.basic_consume(
                queue=RabbitMQSettings.QUEUE_NAME,
                on_message_callback=self.transmitter.send_to_elasticsearch
            )

            self.channel.start_consuming()

        except Exception as e:
            logger.error(f"Error starting receiver: {str(e)}")
            time.sleep(5)

            if self.channel:
                self.channel.stop_consuming()

            if self.connection:
                self.connection.close()

            self.start()

    
    def create_connection(self):
        for _ in range(3):
            try:
                rabbit_params = pika.ConnectionParameters(
                    host=RabbitMQSettings.HOST,
                    port=RabbitMQSettings.PORT
                )
                connection = pika.BlockingConnection(rabbit_params)
                return connection
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
                logger.info("Retrying in 5 seconds...")
                time.sleep(5)

    
    def create_channel(self):
        for _ in range(3):
            try:
                channel = self.connection.channel()
                channel.queue_declare(queue=RabbitMQSettings.QUEUE_NAME)
                return channel
            except Exception as e:
                logger.error(f"Failed to create channel: {str(e)}")
                logger.info("Retrying in 5 seconds...")
                time.sleep(5)