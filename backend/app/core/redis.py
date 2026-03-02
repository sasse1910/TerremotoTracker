import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _pool

    if _pool is None:
        _pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )

    return _pool


async def close_redis() -> None:
    global _pool

    if _pool:
        await _pool.aclose()
        _pool = None


class CacheService:
    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    async def get(self, key: str) -> str | None:
        value = await self._redis.get(key)
        logger.debug("cache_hit" if value else "cache_miss", key=key)
        return value

    async def set(self, key: str, value: str, ttl: int = settings.CACHE_TTL_SECONDS) -> None:
        await self._redis.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def flush_pattern(self, pattern: str) -> int:
        keys = await self._redis.keys(pattern)
        return await self._redis.delete(*keys) if keys else 0
