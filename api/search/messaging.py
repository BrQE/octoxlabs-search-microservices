import json
import pika
from django.conf import settings
from functools import wraps
from django.utils import timezone

class RabbitMQClient:
    def __init__(self):
        self.credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER,
            settings.RABBITMQ_PASSWORD
        )
        self.parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=int(settings.RABBITMQ_PORT),
            virtual_host=settings.RABBITMQ_VHOST,
            credentials=self.credentials
        )
        self.connection = None
        self.channel = None

    def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
             
            # Declare queues
            self.channel.queue_declare(
                queue='search_query_queue',
                durable=True
            )

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def publish_message(self, routing_key, message):
        try:
            self.connect()
            self.channel.basic_publish(
                exchange="",
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
        finally:
            self.close()

def log_search_query(func):
    """Decorator to log search queries to RabbitMQ"""
    @wraps(func)
    def wrapper(view_instance, request, *args, **kwargs):
        client = RabbitMQClient()
        
        # Log the incoming request
        log_data = {
            'ip': request.META.get('REMOTE_ADDR'),
            'username': request.user.username,
            'query': request.data.get('query', ''),
            'timestamp': str(timezone.now()),
        }
        
        try:
            client.publish_message(
                routing_key='search.query.received',
                message=log_data
            )
        except Exception as e:
            print(f"Failed to log search query: {str(e)}")
        
        return func(view_instance, request, *args, **kwargs)
    
    return wrapper 