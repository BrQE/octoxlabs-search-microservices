import requests
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .serializers import SearchQuerySerializer, SearchResultSerializer
from .services import SearchService
from .pagination import SearchPagination
from .throttles import SearchUserRateThrottle, SearchAnonRateThrottle
from .messaging import log_search_query

logger = logging.getLogger(__name__)


class SearchView(APIView):
    pagination_class = SearchPagination
    throttle_classes = [SearchUserRateThrottle, SearchAnonRateThrottle]

    def __init__(self, search_service=None):
        super().__init__()
        self.search_service = search_service or SearchService()
        self.pagination = self.pagination_class()

    @swagger_auto_schema(
        request_body=SearchQuerySerializer,
        responses={
            200: SearchResultSerializer(many=True),
            400: "Bad Request",
            429: "Too Many Requests",
            500: "Internal Server Error",
            503: "Service Unavailable",
        },
        operation_description="Search for hosts using a query string",
        operation_summary="Search hosts",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of results per page",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    @log_search_query
    def post(self, request):
        try:
            # Validate input
            serializer = SearchQuerySerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid input", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Execute search
            query = serializer.validated_data["query"]
            results = self.search_service.search(query)

            # Serialize results
            result_serializer = SearchResultSerializer(data=results, many=True)
            if not result_serializer.is_valid():
                logger.error(f"Invalid search results: {result_serializer.errors}")
                return Response(
                    {"error": "Invalid search results"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Paginate results
            page = self.pagination.paginate_queryset(result_serializer.data, request)
            if page is not None:
                response_data = {"total": len(result_serializer.data), "results": page}
                return Response(response_data)

            response_data = {
                "total": len(result_serializer.data),
                "results": result_serializer.data,
            }
            return Response(response_data)

        except Exception as e:
            logger.error(f"Search failed: {str(e)}", exc_info=True)
            return Response(
                {"error": "Search failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
