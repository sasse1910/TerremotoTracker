from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.earthquake import Earthquake


def _make_earthquake(**kwargs) -> Earthquake:
    defaults = dict(
        usgs_id="us2024test01",
        magnitude=4.5,
        magnitude_type="ml",
        place="10km N of Testville",
        title="M 4.5 - Testville",
        occurred_at=datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC),
        latitude=35.0,
        longitude=-120.0,
        depth_km=8.0,
        tsunami=0,
        created_in_db=datetime.now(tz=UTC),
    )
    defaults.update(kwargs)
    return Earthquake(**defaults)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_earthquakes_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/earthquakes")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_earthquakes_returns_seeded_data(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    db_session.add(_make_earthquake())
    await db_session.commit()

    response = await client.get("/api/v1/earthquakes")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["usgs_id"] == "us2024test01"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_earthquakes_magnitude_filter(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    db_session.add(_make_earthquake(usgs_id="eq_small", magnitude=2.0))
    db_session.add(_make_earthquake(usgs_id="eq_large", magnitude=6.0))
    await db_session.commit()

    response = await client.get("/api/v1/earthquakes?min_magnitude=5.0")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["usgs_id"] == "eq_large"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_earthquakes_bbox_filter(client: AsyncClient, db_session: AsyncSession) -> None:
    db_session.add(_make_earthquake(usgs_id="eq_inside", latitude=10.0, longitude=10.0))
    db_session.add(_make_earthquake(usgs_id="eq_outside", latitude=80.0, longitude=80.0))
    await db_session.commit()

    response = await client.get("/api/v1/earthquakes?bbox=0,0,20,20")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["usgs_id"] == "eq_inside"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_earthquakes_invalid_bbox(client: AsyncClient) -> None:
    response = await client.get("/api/v1/earthquakes?bbox=not,a,valid,bbox")
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_earthquakes_bbox_wrong_part_count(client: AsyncClient) -> None:
    response = await client.get("/api/v1/earthquakes?bbox=1,2,3")
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_earthquakes_pagination(client: AsyncClient, db_session: AsyncSession) -> None:
    for i in range(5):
        db_session.add(
            _make_earthquake(
                usgs_id=f"eq_page_{i:02d}",
                occurred_at=datetime(2024, 1, i + 1, 0, 0, 0, tzinfo=UTC),
            )
        )
    await db_session.commit()

    response = await client.get("/api/v1/earthquakes?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5
    assert len(data["data"]) == 2

    response2 = await client.get("/api/v1/earthquakes?limit=2&offset=2")
    assert len(response2.json()["data"]) == 2


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_earthquake_by_id(client: AsyncClient, db_session: AsyncSession) -> None:
    eq = _make_earthquake()
    db_session.add(eq)
    await db_session.flush()
    eq_id = eq.id
    await db_session.commit()

    response = await client.get(f"/api/v1/earthquakes/{eq_id}")
    assert response.status_code == 200
    assert response.json()["usgs_id"] == "us2024test01"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_earthquake_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/earthquakes/99999")
    assert response.status_code == 404
