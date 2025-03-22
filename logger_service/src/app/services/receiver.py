import pika
import time
from loguru import logger

from ..core.config import settings
from .transmitter import Transmitter


class Receiver:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.transmitter = Transmitter()
        logger.info("Initializing Receiver service")

    def start(self):
        try:
            logger.info("Attempting to start receiver service...")
            self.connection = self.create_connection()
            if self.connection is None:
                logger.error("Failed to connect to RabbitMQ after all retry attempts")
                raise Exception("Failed to connect to RabbitMQ")
        
            self.channel = self.create_channel()
            if self.channel is None:
                logger.error("Failed to create channel after all retry attempts")
                raise Exception("Failed to create channel")
            
            logger.info(f"Successfully connected to RabbitMQ queue: {settings.RABBITMQ_QUEUE_NAME}")
            self.channel.basic_consume(
                queue=settings.RABBITMQ_QUEUE_NAME,
                on_message_callback=self.transmitter.send_to_elasticsearch
            )
            logger.info("Message consumption started")

            self.channel.start_consuming()

        except Exception as e:
            logger.exception(f"Critical error in receiver service: {str(e)}")
            logger.info("Attempting to restart receiver service in 5 seconds...")
            time.sleep(5)

            if self.channel:
                logger.info("Stopping message consumption...")
                self.channel.stop_consuming()

            if self.connection:
                logger.info("Closing RabbitMQ connection...")
                self.connection.close()

            self.start()
    
    def create_connection(self):
        for attempt in range(3):
            try:
                logger.info(f"Attempting to connect to RabbitMQ (attempt {attempt + 1}/3)...")
                credentials = pika.PlainCredentials(
                    username=settings.RABBITMQ_USER,
                    password=settings.RABBITMQ_PASSWORD
                )
                rabbit_params = pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    virtual_host=settings.RABBITMQ_VHOST,
                    credentials=credentials
                )
                connection = pika.BlockingConnection(rabbit_params)
                logger.info("Successfully connected to RabbitMQ")
                return connection
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
                if attempt < 2:
                    logger.info("Retrying in 5 seconds...")
                    time.sleep(5)
    
    def create_channel(self):
        for attempt in range(3):
            try:
                logger.info(f"Attempting to create channel (attempt {attempt + 1}/3)...")
                channel = self.connection.channel()
                channel.queue_declare(queue=settings.RABBITMQ_QUEUE_NAME, durable=True)
                logger.info(f"Successfully created channel and declared queue: {settings.RABBITMQ_QUEUE_NAME}")
                return channel
            except Exception as e:
                logger.error(f"Failed to create channel: {str(e)}")
                if attempt < 2:
                    logger.info("Retrying in 5 seconds...")
                    time.sleep(5)