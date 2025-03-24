from contextlib import asynccontextmanager
from loguru import logger
import threading

from .api import router
from .core.config import settings
from .core.setup import create_application, create_index
from .services.receiver import Receiver
from .services.transmitter import Transmitter


logger.info("Initializing logger service...")
logger.info(f"Environment: {settings.ENVIRONMENT}")
logger.info(f"Elasticsearch server: {settings.ES_SERVER}")
logger.info(f"RabbitMQ host: {settings.RABBITMQ_HOST}")


@asynccontextmanager
async def lifespan(app):
    # Startup
    logger.info("Starting up logger service...")
    transmitter = Transmitter()
    receiver = Receiver(transmitter)
    logger.info("Receiver and Transmitter services initialized")

    # Start receiver in a separate thread
    receiver_thread = threading.Thread(target=receiver.start)
    receiver_thread.daemon = (
        True  # This ensures the thread will be terminated when the main program exits
    )
    receiver_thread.start()

    logger.info("Logger service startup completed")
    yield
    # Shutdown
    receiver.stop()
    logger.info("Shutting down logger service...")


es = create_index(settings=settings)
logger.info("Elasticsearch index created/verified successfully")

app = create_application(router=router, settings=settings, lifespan=lifespan)
logger.info("FastAPI application created successfully")
