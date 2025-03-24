import logging
import sys
from loguru import logger

from .config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Configure logging for the application."""
    # Remove default logger
    logger.remove()

    # Add console handler with custom format
    logger.add(
        sys.stdout, format=settings.LOG_FORMAT, level=settings.LOG_LEVEL, colorize=True
    )

    # Add file handler for errors
    logger.add(
        settings.LOG_FILE,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
    )

    # Intercept standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Set loguru logger as the default
    logging.getLogger().handlers = [InterceptHandler()]
