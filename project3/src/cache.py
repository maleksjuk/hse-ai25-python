from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from config import REDIS_URL, CACHE_EXPIRE_SECONDS

async def init_cache():
    redis = aioredis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

async def invalidate_cache(method: str, route: str):
    key = f"fastapi-cache:{method}:{route}"
    await FastAPICache.get_backend().clear(key=key)
