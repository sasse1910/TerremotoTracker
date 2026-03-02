import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.core.redis import CacheService, close_redis, get_redis

setup_logging()
logger = get_logger(__name__)

_poller_task: asyncio.Task | None = None


async def _usgs_poller() -> None:
    """Background task: poll USGS every 30 s and broadcast new events."""
    from app.api.v1.endpoints.ws import manager
    from app.core.database import AsyncSessionFactory
    from app.services.usgs_service import USGSService

    logger.info("usgs_poller_started")
    while True:
        try:
            await asyncio.sleep(30)
            async with AsyncSessionFactory() as db:
                try:
                    redis_client = await get_redis()
                    cache: CacheService | None = CacheService(redis_client)
                except Exception:
                    cache = None
                service = USGSService(db=db, cache=cache)
                features = await service.fetch_by_period("1h")
            if features:
                await manager.broadcast(json.dumps({"type": "update", "count": len(features)}))
        except asyncio.CancelledError:
            logger.info("usgs_poller_stopped")
            raise
        except Exception as exc:
            logger.warning("usgs_poller_error", error=str(exc))


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _poller_task
    logger.info("app_starting", environment=settings.ENVIRONMENT)
    await get_redis()
    _poller_task = asyncio.create_task(_usgs_poller())
    yield
    if _poller_task:
        _poller_task.cancel()
        try:
            await _poller_task
        except asyncio.CancelledError:
            pass
    await close_redis()
    logger.info("app_stopped")


app = FastAPI(
    title="TerremotoTracker API",
    description="Real-time earthquake and volcano monitor",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1 import router as api_v1_router  # noqa: E402

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.ENVIRONMENT}
