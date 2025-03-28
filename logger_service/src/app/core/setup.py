from typing import Any
from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from loguru import logger

from .logger import setup_logging
from .database import get_elasticsearch_client
from .config import (
    AppSettings,
    EnvironmentOption,
    EnvironmentSettings,
    ElasticsearchSettings,
)


def create_application(
    router: APIRouter,
    settings: AppSettings | EnvironmentSettings,
    **kwargs: Any,
) -> FastAPI:
    """Creates and configures a FastAPI application based on the provided settings.

    This function initializes a FastAPI application and configures it with various settings
    and handlers based on the type of the `settings` object provided.

    Parameters
    ----------
    router : APIRouter
        The APIRouter object containing the routes to be included in the FastAPI application.

    settings
        An instance representing the settings for configuring the FastAPI application.
        It determines the configuration applied:

        - AppSettings: Configures basic app metadata like name, description, contact, and license info.
        - EnvironmentSettings: Conditionally sets documentation URLs and integrates custom routes for API documentation
          based on the environment type.

    **kwargs
        Additional keyword arguments passed directly to the FastAPI constructor.

    Returns
    -------
    FastAPI
        A fully configured FastAPI application instance.

    The function configures the FastAPI application with different features and behaviors
    based on the provided settings. It includes setting up database connections, Redis pools
    for caching, queue, and rate limiting, client-side caching, and customizing the API documentation
    based on the environment settings.
    """
    # Setup logging first
    setup_logging()
    logger.info("Initializing FastAPI application")

    # --- before creating application ---
    if isinstance(settings, AppSettings):
        to_update = {
            "title": settings.APP_NAME,
            "description": settings.APP_DESCRIPTION,
            "contact": {"name": settings.CONTACT_NAME, "email": settings.CONTACT_EMAIL},
            "license_info": {"name": settings.LICENSE_NAME},
        }
        kwargs.update(to_update)

    if isinstance(settings, EnvironmentSettings):
        kwargs.update({"docs_url": None, "redoc_url": None, "openapi_url": None})

    application = FastAPI(**kwargs)
    application.include_router(router)
    logger.info("Router included in application")

    if isinstance(settings, EnvironmentSettings):
        if settings.ENVIRONMENT != EnvironmentOption.PRODUCTION:
            logger.info(
                "Setting up documentation routes for non-production environment"
            )
            docs_router = APIRouter()

            @docs_router.get("/docs", include_in_schema=False)
            async def get_swagger_documentation() -> HTMLResponse:
                return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

            @docs_router.get("/redoc", include_in_schema=False)
            async def get_redoc_documentation() -> HTMLResponse:
                return get_redoc_html(openapi_url="/openapi.json", title="docs")

            @docs_router.get("/openapi.json", include_in_schema=False)
            async def openapi() -> dict[str, Any]:
                out: dict = get_openapi(
                    title=application.title,
                    version=application.version,
                    routes=application.routes,
                )
                return out

            application.include_router(docs_router)
            logger.info("Documentation routes added")

    return application


def create_index(settings: ElasticsearchSettings):
    """Create an Elasticsearch index if it doesn't exist"""
    es = get_elasticsearch_client()
    # Create index if it doesn't exist
    if not es.indices.exists(index=settings.ES_LOG_INDEX_NAME):
        logger.info(f"Creating index '{settings.ES_LOG_INDEX_NAME}'...")
        es.indices.create(
            index=settings.ES_LOG_INDEX_NAME, mappings=settings.ES_LOG_INDEX_MAPPINGS
        )
        logger.info(f"Successfully created index '{settings.ES_LOG_INDEX_NAME}'")
    return es
