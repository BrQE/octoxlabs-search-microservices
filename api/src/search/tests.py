import base64
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User

class SearchViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='octoAdmin')
        self.auth_token = base64.b64encode(b'octoAdmin').decode('utf-8')
        self.client.credentials(HTTP_AUTHORIZATION=f'Octoxlabs {self.auth_token}')
        
    @patch('search.views.requests.post')
    @patch('search.views.Elasticsearch')
    @patch('search.views.pika.BlockingConnection')
    def test_search_success(self, mock_pika, mock_es, mock_requests_post):
        # Mock converter response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": {
                "wildcard": {
                    "Hostname.keyword": "octoxlabs*"
                }
            }
        }
        mock_requests_post.return_value = mock_response
        
        # Mock Elasticsearch response
        mock_es_instance = mock_es.return_value
        mock_es_instance.search.return_value = {
            'hits': {
                'total': {'value': 1},
                'hits': [
                    {
                        '_source': {
                            'Hostname': 'octoxlabs01',
                            'Ip': ['0.0.0.0']
                        }
                    }
                ]
            }
        }
        
        # Mock RabbitMQ connection
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_pika.return_value = mock_connection
        
        # Make request
        response = self.client.post(
            reverse('search'),
            {'query': 'Hostname = octoxlabs*'},
            format='json'
        )
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(len(response.data['results']), 1)
        
        # Verify converter was called
        mock_requests_post.assert_called_once()
        
        # Verify Elasticsearch was called
        mock_es_instance.search.assert_called_once()
        
        # Verify logging was attempted
        mock_channel.queue_declare.assert_called_once()
        mock_channel.basic_publish.assert_called_once()
        
    def test_authentication_failure(self):
        # Remove credentials
        self.client.credentials()
        
        # Make request
        response = self.client.post(
            reverse('search'),
            {'query': 'Hostname = octoxlabs*'},
            format='json'
        )
        
        # Assert authentication failure
        self.assertEqual(response.status_code, 401)
        
    def test_invalid_query(self):
        # Make request with empty query
        response = self.client.post(
            reverse('search'),
            {'query': ''},
            format='json'
        )
        
        # Assert validation error
        self.assertEqual(response.status_code, 400) 