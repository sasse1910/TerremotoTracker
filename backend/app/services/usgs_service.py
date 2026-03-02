import json
from datetime import UTC, datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger
from app.core.redis import CacheService
from app.models.earthquake import Earthquake

logger = get_logger(__name__)

PERIOD_TO_FILE: dict[str, str] = {
    "1h": "all_hour.geojson",
    "24h": "all_day.geojson",
    "7d": "all_week.geojson",
    "30d": "all_month.geojson",
}


class USGSService:
    def __init__(self, db: AsyncSession, cache: CacheService | None = None) -> None:
        self._db = db
        self._cache = cache

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _fetch_geojson(self, url: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    def _parse_feature(self, feature: dict) -> dict | None:
        props = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates") or [None, None, None]

        mag = props.get("mag")
        time_ms = props.get("time")

        if mag is None or time_ms is None:
            return None

        updated_ms = props.get("updated")

        return {
            "usgs_id": feature.get("id"),
            "magnitude": float(mag),
            "magnitude_type": props.get("magType"),
            "place": props.get("place") or "Unknown",
            "title": props.get("title"),
            "occurred_at": datetime.fromtimestamp(time_ms / 1000, tz=UTC),
            "updated_at_usgs": datetime.fromtimestamp(updated_ms / 1000, tz=UTC)
            if updated_ms is not None
            else None,
            "longitude": float(coords[0]) if coords[0] is not None else 0.0,
            "latitude": float(coords[1]) if coords[1] is not None else 0.0,
            "depth_km": float(coords[2]) if coords[2] is not None else None,
            "status": props.get("status"),
            "tsunami": int(props.get("tsunami") or 0),
            "alert": props.get("alert"),
            "url": props.get("url"),
            "detail_url": props.get("detail"),
        }

    async def _upsert_earthquake(self, data: dict) -> Earthquake:
        stmt = select(Earthquake).where(Earthquake.usgs_id == data["usgs_id"])
        result = await self._db.execute(stmt)
        eq = result.scalar_one_or_none()

        if eq:
            for key, value in data.items():
                setattr(eq, key, value)
        else:
            eq = Earthquake(**data)
            self._db.add(eq)

        await self._db.flush()
        return eq

    async def fetch_by_period(self, period: str) -> list[dict]:
        filename = PERIOD_TO_FILE.get(period)
        if not filename:
            raise ValueError(f"Invalid period: {period!r}")

        cache_key = f"earthquakes:{period}"
        features: list[dict] | None = None

        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                logger.info("usgs_cache_hit", period=period)
                features = json.loads(cached)

        if features is None:
            url = f"{settings.USGS_FEED_URL}/{filename}"
            logger.info("usgs_fetch", url=url)
            geojson = await self._fetch_geojson(url)
            features = geojson.get("features") or []

            if self._cache:
                await self._cache.set(cache_key, json.dumps(features))

        count = 0
        for feature in features:
            data = self._parse_feature(feature)
            if data:
                await self._upsert_earthquake(data)
                count += 1

        await self._db.commit()
        logger.info("usgs_upserted", period=period, count=count)
        return features
