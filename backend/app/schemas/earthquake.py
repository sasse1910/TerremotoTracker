from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EarthquakeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usgs_id: str

    magnitude: float
    magnitude_type: str | None

    place: str
    title: str | None

    occurred_at: datetime
    updated_at_usgs: datetime | None

    latitude: float
    longitude: float
    depth_km: float | None

    status: str | None
    tsunami: int
    alert: str | None
    url: str | None
    detail_url: str | None

    created_in_db: datetime


class EarthquakeListResponse(BaseModel):
    count: int
    data: list[EarthquakeOut]
