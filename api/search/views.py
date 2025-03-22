import json
import pika
import requests
import datetime
from django.conf import settings
from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SearchQuerySerializer, SearchResultSerializer
from .messaging import log_search_query


class SearchView(APIView):
    @log_search_query
    def post(self, request):
        serializer = SearchQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query'] 
        
        # Send query to converter service
        try:
            converter_response = requests.post(
                settings.QUERY_CONVERTER_URL,
                json={'query': query}
            )
            
            if converter_response.status_code != 200:
                return Response(
                    {"error": "Query conversion failed", "details": converter_response.text},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            es_query = converter_response.json()
            
            # Connect to Elasticsearch
            es = Elasticsearch(settings.ELASTICSEARCH_HOST)
            
            # Execute search
            search_response = es.search(
                index=settings.ELASTICSEARCH_INDEX,
                body=es_query
            )

            # Extract and validate results
            hits = search_response['hits']['hits']
            results = [hit['_source'] for hit in hits]

            # Serialize results
            result_serializer = SearchResultSerializer(data=results, many=True)
            if not result_serializer.is_valid():
                return Response(
                    {"error": "Invalid search results", "details": result_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result_serializer.data)
        
        except requests.RequestException as e:
            return Response(
                {"error": "Failed to connect to query converter service", "details": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": "Search failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    