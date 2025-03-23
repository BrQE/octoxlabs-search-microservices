from loguru import logger

from .api import router
from .core.config import settings
from .core.setup import create_application

logger.info("Initializing query converter service...")
logger.info(f"Environment: {settings.ENVIRONMENT}")

app = create_application(router=router, settings=settings)