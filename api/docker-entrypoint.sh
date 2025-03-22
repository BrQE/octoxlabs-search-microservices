#!/bin/bash

# Wait for Elasticsearch to be ready
echo "Waiting for Elasticsearch..."
while ! curl -s "$ELASTICSEARCH_HOST" > /dev/null; do
    sleep 1
done

# Wait for RabbitMQ to be ready
echo "Waiting for RabbitMQ..."
until timeout 1 bash -c "cat < /dev/null > /dev/tcp/$RABBITMQ_HOST/$RABBITMQ_PORT"; do
    sleep 1
done

# Apply database migrations
echo "Applying database migrations..."
poetry run python manage.py migrate

# Load dummy data into Elasticsearch
echo "Loading dummy data into Elasticsearch..."
poetry run python manage.py load_dummy_data

# Start server
echo "Starting server..."
poetry run python manage.py runserver 0.0.0.0:8000 