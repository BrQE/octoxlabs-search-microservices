import json
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from django.conf import settings

class Command(BaseCommand):
    help = 'Load dummy data into Elasticsearch'

    def handle(self, *args, **options):
        # Connect to Elasticsearch
        es = Elasticsearch(settings.ELASTICSEARCH_HOST)
        
        # Define the index mapping
        mapping = {
            "mappings": {
                "properties": {
                    "Hostname": {
                        "type": "keyword"
                    },
                    "Ip": {
                        "type": "keyword"
                    }
                }
            }
        }

        # Sample data
        dummy_data = [
            {
                "Hostname": "octoxlabs01",
                "Ip": ["192.168.1.101", "10.0.0.101"]
            },
            {
                "Hostname": "octoxlabs02",
                "Ip": ["192.168.1.102"]
            },
            {
                "Hostname": "octoxlabs-prod01",
                "Ip": ["10.0.1.101", "10.0.2.101"]
            },
            {
                "Hostname": "octoxlabs-prod02",
                "Ip": ["10.0.1.102"]
            },
            {
                "Hostname": "octoxlabs-dev01",
                "Ip": ["172.16.1.101"]
            },
            {
                "Hostname": "octoxlabs-staging01",
                "Ip": ["172.16.2.101", "172.16.2.102"]
            }
        ]

        # Create index with mapping
        try:
            # Delete index if exists
            if es.indices.exists(index=settings.ELASTICSEARCH_INDEX):
                self.stdout.write(f"Deleting existing index '{settings.ELASTICSEARCH_INDEX}'...")
                es.indices.delete(index=settings.ELASTICSEARCH_INDEX)

            # Create new index with mapping
            self.stdout.write(f"Creating index '{settings.ELASTICSEARCH_INDEX}' with mapping...")
            es.indices.create(
                index=settings.ELASTICSEARCH_INDEX,
                body=mapping
            )

            # Bulk insert data
            bulk_data = []
            for item in dummy_data:
                bulk_data.append({"index": {"_index": settings.ELASTICSEARCH_INDEX}})
                bulk_data.append(item)

            es.bulk(body=bulk_data, refresh=True)
            
            # Verify the data
            count = es.count(index=settings.ELASTICSEARCH_INDEX)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully loaded {count['count']} documents into '{settings.ELASTICSEARCH_INDEX}'"
                )
            )

            # Show sample query
            self.stdout.write("\nSample query to test:")
            self.stdout.write(
                'curl -X POST http://localhost:8000/api/search/ '
                '-H "Authorization: Octoxlabs b2N0b0FkbWlu" '
                '-H "Content-Type: application/json" '
                '-d \'{"query": "Hostname = octoxlabs*"}\''
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error: {str(e)}")
            ) 