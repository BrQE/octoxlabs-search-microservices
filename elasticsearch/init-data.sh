#!/bin/bash

# Wait for Elasticsearch to be ready
until curl -s http://localhost:9200 > /dev/null; do
    echo "Waiting for Elasticsearch..."
    sleep 1
done

echo "Elasticsearch is up and running!"

# Create index with mapping
curl -X PUT "localhost:9200/octoxlabsdata" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "Hostname": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "Ip": {
        "type": "text"
      }
    }
  }
}
'

# Insert sample data
curl -X POST "localhost:9200/octoxlabsdata/_doc" -H 'Content-Type: application/json' -d'
{
  "Hostname": "octoxlabs01",
  "Ip": ["0.0.0.0"]
}
'

curl -X POST "localhost:9200/octoxlabsdata/_doc" -H 'Content-Type: application/json' -d'
{
  "Hostname": "octoxlabs02",
  "Ip": ["1.1.1.1"]
}
'

curl -X POST "localhost:9200/octoxlabsdata/_doc" -H 'Content-Type: application/json' -d'
{
  "Hostname": "octoxlabs03",
  "Ip": ["2.2.2.2"]
}
'

# Refresh index to make data immediately available
curl -X POST "localhost:9200/octoxlabsdata/_refresh"

echo "Sample data loaded successfully!" 