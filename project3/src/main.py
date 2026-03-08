from fastapi import FastAPI
import uvicorn
import logging
import asyncio
from contextlib import asynccontextmanager
from api import base, extra

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

cleanup_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global cleanup_task
    cleanup_task = asyncio.create_task(extra.cleanup_unused_links())
    logger.info("Created task 'cleanup_unused_links'")
    yield
    if cleanup_task:
        cleanup_task.cancel()
        logger.info("Canceled task 'cleanup_unused_links'")


app = FastAPI(lifespan=lifespan)
app.include_router(extra.router)
app.include_router(base.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="info")
