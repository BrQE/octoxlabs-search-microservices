import base64
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import requests


class SearchViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="octoAdmin")
        self.auth_token = base64.b64encode(b"octoAdmin").decode("utf-8")
        self.client.credentials(HTTP_AUTHORIZATION=f"Octoxlabs {self.auth_token}")

    @patch("search.services.requests.post")
    @patch("search.services.Elasticsearch")
    @patch("search.messaging.pika.BlockingConnection")
    def test_search_success(self, mock_pika, mock_es, mock_requests_post):
        # Mock converter response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": {"wildcard": {"Hostname.keyword": "octoxlabs*"}}
        }
        mock_requests_post.return_value = mock_response

        # Mock Elasticsearch response
        mock_es.return_value.search.return_value = {
            "hits": {
                "hits": [
                    {"_source": {"Hostname": "octoxlabs-host1", "Ip": ["192.168.1.1"]}},
                    {"_source": {"Hostname": "octoxlabs-host2", "Ip": ["192.168.1.2"]}},
                    {"_source": {"Hostname": "octoxlabs-host3", "Ip": ["192.168.1.3"]}},
                    {"_source": {"Hostname": "octoxlabs-host4", "Ip": ["192.168.1.4"]}},
                    {"_source": {"Hostname": "octoxlabs-host5", "Ip": ["192.168.1.5"]}},
                    {"_source": {"Hostname": "octoxlabs-host6", "Ip": ["192.168.1.6"]}},
                ],
                "total": {"value": 6},
            }
        }

        # Mock RabbitMQ connection
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_pika.return_value = mock_connection

        # Make request
        response = self.client.post(
            reverse("search"), {"query": "Hostname = octoxlabs*"}, format="json"
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total"], 6)
        self.assertEqual(len(response.data["results"]), 6)

        # Verify converter was called
        mock_requests_post.assert_called_once()

        # Verify Elasticsearch was called
        mock_es.return_value.search.assert_called_once()

        # Verify logging was attempted
        mock_channel.queue_declare.assert_called_once()
        mock_channel.basic_publish.assert_called_once()

    def test_authentication_failure(self):
        # Remove credentials
        self.client.credentials()

        # Make request
        response = self.client.post(
            reverse("search"), {"query": "Hostname = octoxlabs*"}, format="json"
        )

        # Assert authentication failure
        self.assertEqual(response.status_code, 403)

    def test_invalid_query(self):
        # Make request with empty query
        response = self.client.post(reverse("search"), {"query": ""}, format="json")

        # Assert validation error
        self.assertEqual(response.status_code, 400)

    @patch("search.services.requests.post")
    @patch("search.services.Elasticsearch")
    @patch("search.messaging.pika.BlockingConnection")
    def test_pagination(self, mock_pika, mock_es, mock_requests_post):
        # Mock converter response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"query": {"match_all": {}}}
        mock_requests_post.return_value = mock_response

        # Mock Elasticsearch response with real data structure
        mock_es_instance = mock_es.return_value
        mock_es_instance.search.return_value = {
            "hits": {
                "total": {"value": 6},
                "hits": [
                    {
                        "_source": {
                            "Hostname": "octoxlabs01",
                            "Ip": ["192.168.1.101", "10.0.0.101"],
                        }
                    },
                    {"_source": {"Hostname": "octoxlabs02", "Ip": ["192.168.1.102"]}},
                    {
                        "_source": {
                            "Hostname": "octoxlabs-prod01",
                            "Ip": ["10.0.1.101", "10.0.2.101"],
                        }
                    },
                    {"_source": {"Hostname": "octoxlabs-prod02", "Ip": ["10.0.1.102"]}},
                    {
                        "_source": {
                            "Hostname": "octoxlabs-dev01",
                            "Ip": ["172.16.1.101"],
                        }
                    },
                    {
                        "_source": {
                            "Hostname": "octoxlabs-staging01",
                            "Ip": ["172.16.2.101", "172.16.2.102"],
                        }
                    },
                ],
            }
        }

        # Test first page
        response = self.client.post(
            f"{reverse('search')}?page=1&page_size=10",
            {"query": "Hostname = octoxlabs*"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total"], 6)
        self.assertEqual(len(response.data["results"]), 6)

        # Test second page (should fail as there are no more results)
        response = self.client.post(
            f"{reverse('search')}?page=2&page_size=10",
            {"query": "Hostname = octoxlabs*"},
            format="json",
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Search failed")
        self.assertEqual(response.data["details"], "Invalid page.")

    def test_invalid_query_patterns(self):
        # Test SQL injection pattern
        response = self.client.post(
            reverse("search"),
            {"query": "Hostname = octoxlabs; DROP TABLE users;"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

        # Test query too short
        response = self.client.post(reverse("search"), {"query": "H="}, format="json")
        self.assertEqual(response.status_code, 400)

        # Test invalid field
        response = self.client.post(
            reverse("search"), {"query": "invalid_field = value"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    @patch("search.services.requests.post")
    def test_converter_service_error(self, mock_requests_post):
        # Mock converter service error
        mock_requests_post.side_effect = requests.RequestException(
            "Service unavailable"
        )

        response = self.client.post(
            reverse("search"), {"query": "Hostname = octoxlabs*"}, format="json"
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.data)

    @patch("search.services.requests.post")
    @patch("search.services.Elasticsearch")
    def test_elasticsearch_error(self, mock_es, mock_requests_post):
        # Mock converter response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"query": {"match_all": {}}}
        mock_requests_post.return_value = mock_response

        # Mock Elasticsearch error
        mock_es_instance = mock_es.return_value
        mock_es_instance.search.side_effect = Exception("Elasticsearch error")

        response = self.client.post(
            reverse("search"), {"query": "Hostname = octoxlabs*"}, format="json"
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.data)

    @patch("search.messaging.pika.BlockingConnection")
    @patch("search.services.Elasticsearch")
    @patch("search.services.requests.post")
    def test_rabbitmq_logging_failure(self, mock_requests_post, mock_es, mock_pika):
        # Mock converter response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": {"wildcard": {"Hostname.keyword": "octoxlabs*"}}
        }
        mock_requests_post.return_value = mock_response

        # Mock Elasticsearch response
        mock_es.return_value.search.return_value = {
            "hits": {
                "hits": [
                    {"_source": {"Hostname": "octoxlabs-host1", "Ip": ["192.168.1.1"]}}
                ],
                "total": {"value": 1},
            }
        }

        # Mock RabbitMQ connection failure
        mock_pika.side_effect = Exception("RabbitMQ connection failed")

        # Make request
        response = self.client.post(
            reverse("search"), {"query": "Hostname = octoxlabs*"}, format="json"
        )

        # Verify response is successful despite RabbitMQ failure
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total"], 1)
        self.assertEqual(len(response.data["results"]), 1)

        # Verify RabbitMQ connection was attempted
        mock_pika.assert_called_once()
