#!/bin/bash

# Function to check and create .env files
setup_env_files() {
    local service_dirs=("api" "logger_service" "query_converter")
    
    for dir in "${service_dirs[@]}"; do
        if [ ! -f "$dir/.env" ] && [ -f "$dir/.env.example" ]; then
            echo "Creating .env file for $dir from .env.example"
            cp "$dir/.env.example" "$dir/.env"
        fi
    done
}

# Function to wait for services to be ready
wait_for_services() {
    echo "Waiting for all services to be ready..."

    # Wait for Logger service
    while ! curl -s http://localhost:8001/health > /dev/null; do
        echo "Waiting for Logger service to be ready..."
        sleep 5
    done
    echo "Logger service is ready!"
    
    # Wait for Query Converter service
    while ! curl -s http://localhost:8002/health > /dev/null; do
        echo "Waiting for Query Converter service to be ready..."
        sleep 5
    done
    echo "Query Converter service is ready!"
    
    # Wait for API service
    while ! curl -s http://localhost:8000/health > /dev/null; do
        echo "Waiting for API service to be ready..."
        sleep 5
    done
    echo "API service is ready!"

    
    echo "All services are ready!"
}

# Main execution
echo "Setting up environment files..."
setup_env_files

echo "Stopping existing containers..."
docker-compose down

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be ready..."
wait_for_services

echo "Creating superuser..."
docker-compose exec api python src/manage.py createsuperuser --username octoAdmin --email admin@octoxlabs.com --noinput

echo "Testing search endpoint..."
curl -X POST \
  'http://localhost:8000/search/?page=1&page_size=10' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Octoxlabs b2N0b0FkbWlu' \
  -d '{
    "query": "Hostname = octoxlabs*"
}'

echo "Setup complete!" 