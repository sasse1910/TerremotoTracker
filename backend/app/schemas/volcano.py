from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VolcanoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    gvp_id: str

    name: str
    country: str | None
    region: str | None
    subregion: str | None

    latitude: float
    longitude: float
    elevation_m: int | None

    volcano_type: str | None
    last_eruption_year: int | None

    is_active: bool
    activity_level: str | None

    description: str | None
    wikipedia_url: str | None

    created_in_db: datetime
    last_updated: datetime | None


class VolcanoListResponse(BaseModel):
    count: int
    data: list[VolcanoOut]
