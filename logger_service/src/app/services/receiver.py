import pika
import time
import random
from typing import Optional
from pika.exceptions import (
    AMQPConnectionError,
    AMQPChannelError,
    ConnectionClosedByBroker,
    ChannelWrongStateError,
)
from loguru import logger

from ..core.config import settings
from .transmitter import Transmitter


class Receiver:
    def __init__(self, transmitter: Optional[Transmitter] = None):
        """
        Initialize the Receiver service

        Args:
            transmitter: Optional Transmitter instance for dependency injection
        """
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.transmitter = transmitter or Transmitter()
        self._should_stop = False
        logger.info("Initializing Receiver service")

    def start(self) -> None:
        """Start the receiver service with exponential backoff retry"""
        while not self._should_stop:
            try:
                logger.info("Attempting to start receiver service...")
                self._connect_to_rabbitmq()

                logger.info(
                    f"Successfully connected to RabbitMQ queue: {settings.RABBITMQ_QUEUE_NAME}"
                )
                self.channel.basic_consume(
                    queue=settings.RABBITMQ_QUEUE_NAME,
                    on_message_callback=self.transmitter.send_to_elasticsearch,
                )
                logger.info("Message consumption started")

                self.channel.start_consuming()

            except (AMQPConnectionError, ConnectionClosedByBroker) as e:
                logger.exception(f"Connection error in receiver service: {str(e)}")
                self._handle_connection_error()
            except (AMQPChannelError, ChannelWrongStateError) as e:
                logger.exception(f"Channel error in receiver service: {str(e)}")
                self._handle_channel_error()
            except Exception as e:
                logger.exception(f"Unexpected error in receiver service: {str(e)}")
                self._handle_unexpected_error()

    def _connect_to_rabbitmq(self) -> None:
        """Establish connection to RabbitMQ and create channel"""
        try:
            self.connection = self._create_connection()
            if self.connection is None:
                logger.error("Failed to connect to RabbitMQ after all retry attempts")
                raise AMQPConnectionError("Failed to connect to RabbitMQ")

            self.channel = self._create_channel()
            if self.channel is None:
                logger.error("Failed to create channel after all retry attempts")
                raise AMQPChannelError("Failed to create channel")
        except Exception as e:
            logger.exception(f"Error connecting to RabbitMQ: {str(e)}")
            self._cleanup()
            raise

    def _handle_connection_error(self) -> None:
        """Handle connection errors with exponential backoff"""
        self._cleanup()
        self._exponential_backoff_retry()

    def _handle_channel_error(self) -> None:
        """Handle channel errors"""
        self._cleanup_channel()
        self._exponential_backoff_retry()

    def _handle_unexpected_error(self) -> None:
        """Handle unexpected errors"""
        self._cleanup()
        self._exponential_backoff_retry()

    def _cleanup(self) -> None:
        """Clean up all connections"""
        self._cleanup_channel()
        if self.connection and not self.connection.is_closed:
            try:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
            except Exception as e:
                logger.error(f"Error closing RabbitMQ connection: {str(e)}")
            finally:
                self.connection = None

    def _cleanup_channel(self) -> None:
        """Clean up channel"""
        if self.channel and not self.channel.is_closed:
            try:
                self.channel.close()
                logger.info("RabbitMQ channel closed")
            except Exception as e:
                logger.error(f"Error closing RabbitMQ channel: {str(e)}")
            finally:
                self.channel = None

    def _exponential_backoff_retry(self) -> None:
        """Implement exponential backoff retry with jitter"""
        retry_count = 0
        max_retries = 5
        base_delay = 5  # seconds

        while retry_count < max_retries and not self._should_stop:
            # Add jitter to prevent thundering herd problem
            delay = base_delay * (2**retry_count) + random.uniform(0, 1)
            logger.info(
                f"Retrying in {delay:.2f} seconds... (attempt {retry_count + 1}/{max_retries})"
            )
            time.sleep(delay)
            retry_count += 1

    def stop(self) -> None:
        """Gracefully stop the receiver service"""
        self._should_stop = True
        if self.channel and not self.channel.is_closed:
            try:
                self.channel.stop_consuming()
                logger.info("Stopped consuming messages")
            except Exception as e:
                logger.error(f"Error stopping consumption: {str(e)}")
        self._cleanup()
        logger.info("Receiver service stopped")

    def _create_connection(self) -> Optional[pika.BlockingConnection]:
        """
        Create a RabbitMQ connection

        Returns:
            Optional[pika.BlockingConnection]: A new connection to RabbitMQ or None if failed
        """
        try:
            credentials = pika.PlainCredentials(
                username=settings.RABBITMQ_USER, password=settings.RABBITMQ_PASSWORD
            )
            rabbit_params = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                virtual_host=settings.RABBITMQ_VHOST,
                credentials=credentials,
                heartbeat=settings.RABBITMQ_HEARTBEAT,
                blocked_connection_timeout=settings.RABBITMQ_BLOCKED_CONNECTION_TIMEOUT,
            )
            connection = pika.BlockingConnection(rabbit_params)
            logger.info("Successfully connected to RabbitMQ")
            return connection
        except Exception as e:
            logger.error(f"Failed to create RabbitMQ connection: {str(e)}")
            return None

    def _create_channel(self) -> Optional[pika.channel.Channel]:
        """
        Create a RabbitMQ channel

        Returns:
            Optional[pika.channel.Channel]: A new channel or None if failed
        """
        try:
            channel = self.connection.channel()
            channel.queue_declare(queue=settings.RABBITMQ_QUEUE_NAME, durable=True)
            # Add prefetch to control the number of unacknowledged messages
            channel.basic_qos(
                prefetch_count=(
                    settings.RABBITMQ_PREFETCH_COUNT
                    if hasattr(settings, "RABBITMQ_PREFETCH_COUNT")
                    else 1
                )
            )
            logger.info(
                f"Successfully created channel and declared queue: {settings.RABBITMQ_QUEUE_NAME}"
            )
            return channel
        except Exception as e:
            logger.error(f"Failed to create RabbitMQ channel: {str(e)}")
            return None
