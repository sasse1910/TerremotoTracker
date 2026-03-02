from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import CacheService, get_redis
from app.models.earthquake import Earthquake
from app.schemas.earthquake import EarthquakeListResponse, EarthquakeOut
from app.services.usgs_service import USGSService

router = APIRouter()


@router.get("", response_model=EarthquakeListResponse)
async def list_earthquakes(
    min_magnitude: float | None = Query(default=None, ge=0, le=10),
    period: str | None = Query(default=None, pattern="^(1h|24h|7d|30d)$"),
    bbox: str | None = Query(default=None, description="lon_min,lat_min,lon_max,lat_max"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> EarthquakeListResponse:
    lon_min = lat_min = lon_max = lat_max = None
    if bbox is not None:
        parts = bbox.split(",")
        if len(parts) != 4:
            raise HTTPException(
                status_code=400,
                detail="Invalid bbox format. Expected: lon_min,lat_min,lon_max,lat_max",
            )
        try:
            lon_min, lat_min, lon_max, lat_max = (float(p) for p in parts)
        except ValueError as err:
            raise HTTPException(
                status_code=400,
                detail="Invalid bbox values. All coordinates must be numeric.",
            ) from err

    def _apply_filters(stmt):
        if min_magnitude is not None:
            stmt = stmt.where(Earthquake.magnitude >= min_magnitude)
        if lon_min is not None:
            stmt = (
                stmt.where(Earthquake.longitude >= lon_min)
                .where(Earthquake.longitude <= lon_max)
                .where(Earthquake.latitude >= lat_min)
                .where(Earthquake.latitude <= lat_max)
            )
        return stmt

    base_stmt = _apply_filters(select(Earthquake))

    check = await db.execute(base_stmt.limit(1))
    if check.scalar_one_or_none() is None and period:
        try:
            redis_client = await get_redis()
            cache: CacheService | None = CacheService(redis_client)
        except Exception:
            cache = None
        service = USGSService(db=db, cache=cache)
        await service.fetch_by_period(period)

    total_result = await db.execute(_apply_filters(select(func.count()).select_from(Earthquake)))
    total: int = total_result.scalar_one()

    data_result = await db.execute(
        _apply_filters(select(Earthquake))
        .order_by(Earthquake.occurred_at.desc())
        .offset(offset)
        .limit(limit)
    )
    earthquakes = data_result.scalars().all()

    return EarthquakeListResponse(count=total, data=list(earthquakes))


@router.get("/{earthquake_id}", response_model=EarthquakeOut)
async def get_earthquake(
    earthquake_id: int,
    db: AsyncSession = Depends(get_db),
) -> EarthquakeOut:
    result = await db.execute(select(Earthquake).where(Earthquake.id == earthquake_id))
    eq = result.scalar_one_or_none()
    if eq is None:
        raise HTTPException(status_code=404, detail="Earthquake not found")
    return eq
