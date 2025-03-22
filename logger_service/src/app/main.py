from .api import router
from .core.config import settings
from .core.setup import create_application, create_index
from .services.receiver import Receiver
from loguru import logger

logger.info("Initializing logger service...")
logger.info(f"Environment: {settings.ENVIRONMENT}")
logger.info(f"Elasticsearch server: {settings.ES_SERVER}")
logger.info(f"RabbitMQ host: {settings.RABBITMQ_HOST}")

es = create_index(settings=settings)
logger.info("Elasticsearch index created/verified successfully")

app = create_application(router=router, settings=settings)
logger.info("FastAPI application created successfully")

receiver = Receiver()
logger.info("Receiver service initialized")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up logger service...")
    receiver.start()
    logger.info("Logger service startup completed")
