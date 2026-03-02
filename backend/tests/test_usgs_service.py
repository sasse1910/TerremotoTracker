from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.models.earthquake import Earthquake
from app.services.usgs_service import USGSService

VALID_FEATURE = {
    "id": "us2024abcd",
    "properties": {
        "mag": 5.2,
        "magType": "mw",
        "place": "10km N of Somewhere",
        "title": "M 5.2 - 10km N of Somewhere",
        "time": 1_700_000_000_000,
        "updated": 1_700_001_000_000,
        "status": "reviewed",
        "tsunami": 0,
        "alert": None,
        "url": "https://earthquake.usgs.gov/earthquakes/eventpage/us2024abcd",
        "detail": "https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=us2024abcd",
    },
    "geometry": {"type": "Point", "coordinates": [-120.5, 35.8, 10.0]},
}

MISSING_MAG_FEATURE = {
    "id": "us2024efgh",
    "properties": {"mag": None, "time": 1_700_000_000_000, "place": "Somewhere"},
    "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 0.0]},
}

MISSING_TIME_FEATURE = {
    "id": "us2024ijkl",
    "properties": {"mag": 3.0, "time": None, "place": "Somewhere"},
    "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 0.0]},
}

FAKE_GEOJSON = {"type": "FeatureCollection", "features": [VALID_FEATURE]}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_parse_valid_feature(db_session):
    service = USGSService(db=db_session)
    result = service._parse_feature(VALID_FEATURE)

    assert result is not None
    assert result["usgs_id"] == "us2024abcd"
    assert result["magnitude"] == 5.2
    assert result["magnitude_type"] == "mw"
    assert result["place"] == "10km N of Somewhere"
    assert result["longitude"] == -120.5
    assert result["latitude"] == 35.8
    assert result["depth_km"] == 10.0
    assert result["tsunami"] == 0
    assert isinstance(result["occurred_at"], datetime)
    assert result["occurred_at"].tzinfo is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_parse_missing_mag_returns_none(db_session):
    service = USGSService(db=db_session)
    assert service._parse_feature(MISSING_MAG_FEATURE) is None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_parse_missing_time_returns_none(db_session):
    service = USGSService(db=db_session)
    assert service._parse_feature(MISSING_TIME_FEATURE) is None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_parse_missing_updated_field(db_session):
    feature = {
        "id": "us2024xyz",
        "properties": {"mag": 2.5, "time": 1_700_000_000_000, "place": "Somewhere"},
        "geometry": {"type": "Point", "coordinates": [10.0, 20.0, 5.0]},
    }
    service = USGSService(db=db_session)
    result = service._parse_feature(feature)
    assert result is not None
    assert result["updated_at_usgs"] is None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_upsert_creates_new_record(db_session):
    service = USGSService(db=db_session)
    data = service._parse_feature(VALID_FEATURE)
    assert data is not None

    await service._upsert_earthquake(data)
    await db_session.commit()

    result = await db_session.execute(select(Earthquake).where(Earthquake.usgs_id == "us2024abcd"))
    stored = result.scalar_one_or_none()
    assert stored is not None
    assert stored.magnitude == 5.2
    assert stored.place == "10km N of Somewhere"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_upsert_updates_existing_record(db_session):
    service = USGSService(db=db_session)
    data = service._parse_feature(VALID_FEATURE)
    assert data is not None

    await service._upsert_earthquake(data)
    await db_session.commit()

    data["magnitude"] = 6.0
    await service._upsert_earthquake(data)
    await db_session.commit()

    result = await db_session.execute(select(Earthquake).where(Earthquake.usgs_id == "us2024abcd"))
    records = result.scalars().all()
    assert len(records) == 1
    assert records[0].magnitude == 6.0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fetch_by_period_upserts_data(db_session, fake_cache):
    service = USGSService(db=db_session, cache=fake_cache)

    with patch.object(service, "_fetch_geojson", new=AsyncMock(return_value=FAKE_GEOJSON)):
        features = await service.fetch_by_period("24h")

    assert len(features) == 1
    result = await db_session.execute(select(Earthquake))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].usgs_id == "us2024abcd"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fetch_by_period_uses_cache_on_second_call(db_session, fake_cache):
    service = USGSService(db=db_session, cache=fake_cache)
    mock_fetch = AsyncMock(return_value=FAKE_GEOJSON)

    with patch.object(service, "_fetch_geojson", new=mock_fetch):
        await service.fetch_by_period("24h")
        await service.fetch_by_period("24h")

    assert mock_fetch.call_count == 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fetch_by_period_invalid_period(db_session):
    service = USGSService(db=db_session)
    with pytest.raises(ValueError, match="Invalid period"):
        await service.fetch_by_period("999d")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fetch_by_period_skips_invalid_features(db_session, fake_cache):
    geojson = {
        "type": "FeatureCollection",
        "features": [VALID_FEATURE, MISSING_MAG_FEATURE, MISSING_TIME_FEATURE],
    }
    service = USGSService(db=db_session, cache=fake_cache)

    with patch.object(service, "_fetch_geojson", new=AsyncMock(return_value=geojson)):
        await service.fetch_by_period("1h")

    result = await db_session.execute(select(Earthquake))
    rows = result.scalars().all()
    assert len(rows) == 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_fetch_by_period_no_cache(db_session):
    service = USGSService(db=db_session, cache=None)

    with patch.object(service, "_fetch_geojson", new=AsyncMock(return_value=FAKE_GEOJSON)):
        features = await service.fetch_by_period("7d")

    assert len(features) == 1
