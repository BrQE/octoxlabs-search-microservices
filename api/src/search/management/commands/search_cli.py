import base64
import json
import requests
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "CLI tool to search using the API"

    def add_arguments(self, parser):
        parser.add_argument(
            "query", type=str, help='Search query (e.g., "Hostname = octoxlabs*")'
        )
        parser.add_argument(
            "--username",
            type=str,
            default="octoAdmin",
            help="Username for authentication",
        )
        parser.add_argument("--page", type=int, default=1, help="Page number")
        parser.add_argument(
            "--page-size", type=int, default=10, help="Results per page"
        )

    def handle(self, *args, **options):
        query = options["query"]
        username = options["username"]
        page = options["page"]
        page_size = options["page_size"]

        User.objects.get_or_create(username=username)

        # Create auth token
        auth_token = f"Octoxlabs {base64.b64encode(username.encode()).decode()}"

        # Make request to API
        try:
            response = requests.post(
                "http://api:8000/search/",
                json={"query": query},
                params={"page": page, "page_size": page_size},
                headers={"Authorization": auth_token},
            )

            if response.status_code == 200:
                data = response.json()
                self.stdout.write(self.style.SUCCESS(f"Found {data['total']} results:"))
                for hit in data["results"]:
                    self.stdout.write(json.dumps(hit, indent=2))
            else:
                self.stdout.write(self.style.ERROR(f"Error: {response.text}"))

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Request failed: {str(e)}"))
