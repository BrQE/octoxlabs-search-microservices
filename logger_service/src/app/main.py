from .api import router
from .core.config import settings
from .core.setup import create_application, create_index
from .services.receiver import Receiver

es = create_index(settings=settings)
app = create_application(router=router, settings=settings)

receiver = Receiver()

@app.on_event("startup")
async def startup_event():
    receiver.start()
