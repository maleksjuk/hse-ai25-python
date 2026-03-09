import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI
import uvicorn
import logging
import asyncio
from contextlib import asynccontextmanager
from api import base, extra
from auth.users import fastapi_users, auth_backend
from auth.schemas import UserRead, UserCreate
from cache import init_cache, FastAPICache


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
    await init_cache()
    logger.info("Redis cache init")

    yield

    if cleanup_task:
        cleanup_task.cancel()
        logger.info("Canceled task 'cleanup_unused_links'")
    await FastAPICache.clear()
    logger.info("Redis cache clear")



app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(extra.router)

app.include_router(base.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="info")
