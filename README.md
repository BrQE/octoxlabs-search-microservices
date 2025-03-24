# Octoxlabs Senior Backend Engineer Case Study

This project is a solution developed for the Octoxlabs Senior Backend Engineer case study.

## Project Structure

The project is a Docker composition consisting of the following services:

1. **Django REST Framework API**: Main endpoint
2. **Query Converter Service**: FastAPI-based service that converts queries to Elasticsearch format
3. **Logger Service**: Custom-developed service for query logging
4. **RabbitMQ**: Message queue service
5. **Elasticsearch**: Data storage and search service

## Installation and Setup

### Prerequisites

- Docker and Docker Compose

### Running the Project

You can run the project in two ways:

#### 1. Using dev_run.sh (Recommended)

```bash
# Clone the project
git clone https://github.com/BrQE/octoxlabs-search-microservices
cd octoxlabs-search-microservices

# Make the script executable
chmod +x dev_run.sh

# Run the development script
./dev_run.sh
```

This script will:
- Check and create necessary .env files from .env.example files
- Stop any running containers
- Start all services
- Wait for all services to be ready
- Test the search endpoint

#### 2. Manual Setup

```bash
# Clone the project
git clone https://github.com/BrQE/octoxlabs-search-microservices
cd octoxlabs-search-microservices

# Start services using Docker Compose
docker-compose up -d

# Wait for services to start
sleep 30

# Create test user
docker-compose exec api python src/manage.py createsuperuser --username octoAdmin --email admin@octoxlabs.com --noinput
```

## API Usage

### Authentication

The API uses the Octoxlabs authentication mechanism. A token is generated by base64 encoding the username.

```bash
# Token generation example
echo -n "octoAdmin" | base64
# Output: b2N0b0FkbWlu

# API request examples
curl -X POST \
  http://localhost:8000/search \
  -H 'Authorization: Octoxlabs b2N0b0FkbWlu' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Hostname = octoxlabs*"}'

# API request for pagination
url -X POST \
  'http://localhost:8000/search/?page=1&page_size=10' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Octoxlabs b2N0b0FkbWlu' \
  -d '{
    "query": "Hostname = octoxlabs*"
}'
```

### CLI Tool

A CLI tool is available as a Django management command:

```bash
# Using the CLI tool
docker-compose exec api python src/manage.py search_cli "Hostname = octoxlabs*" --username octoAdmin
```

## Security Features

1. **Authentication**: Custom Octoxlabs authentication mechanism
2. **Input Validation**: All API inputs are validated
3. **Error Handling**: Secure error handling and logging
4. **Inter-Service Security**: Isolated services within Docker network

## Testing

To run unit tests:

```bash
docker-compose exec api pytest src/search/tests.py -v
```

## Code Quality

Code quality tools (flake8, black) are integrated:

```bash
# Check code style
docker-compose exec api flake8

# Format code
docker-compose exec api black .
```

## Service Ports

- API Service: 8000
- Query Converter Service: 8001
- Logger Service: 8002
- RabbitMQ: 5672 (AMQP), 15672 (Management UI)
- Elasticsearch: 9200
- Kibana: 5601

## Development

The project uses a microservices architecture with the following key components:

- **API Service**: Handles HTTP requests and authentication
- **Query Converter**: Transforms user queries into Elasticsearch format
- **Logger Service**: Records search queries and results
- **Message Queue**: Manages asynchronous communication between services
- **Search Engine**: Provides efficient data storage and retrieval

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request