from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.volcano import Volcano


def _make_volcano(**kwargs) -> Volcano:
    defaults = dict(
        gvp_id="V001",
        name="Mount Test",
        country="Testland",
        latitude=0.0,
        longitude=0.0,
        is_active=True,
        created_in_db=datetime.now(tz=UTC),
    )
    defaults.update(kwargs)
    return Volcano(**defaults)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_volcanoes_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/volcanoes")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_volcanoes_returns_seeded_data(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    db_session.add(_make_volcano())
    await db_session.commit()

    response = await client.get("/api/v1/volcanoes")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["name"] == "Mount Test"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_volcanoes_active_filter(client: AsyncClient, db_session: AsyncSession) -> None:
    db_session.add(_make_volcano(gvp_id="V_active", name="Active Volcano", is_active=True))
    db_session.add(_make_volcano(gvp_id="V_dormant", name="Dormant Volcano", is_active=False))
    await db_session.commit()

    response = await client.get("/api/v1/volcanoes?is_active=true")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["name"] == "Active Volcano"

    response2 = await client.get("/api/v1/volcanoes?is_active=false")
    assert response2.json()["count"] == 1
    assert response2.json()["data"][0]["name"] == "Dormant Volcano"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_volcanoes_country_filter(client: AsyncClient, db_session: AsyncSession) -> None:
    db_session.add(_make_volcano(gvp_id="V_jp", name="Fuji", country="Japan"))
    db_session.add(_make_volcano(gvp_id="V_it", name="Etna", country="Italy"))
    await db_session.commit()

    response = await client.get("/api/v1/volcanoes?country=japan")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["name"] == "Fuji"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_volcanoes_pagination(client: AsyncClient, db_session: AsyncSession) -> None:
    for i in range(5):
        db_session.add(_make_volcano(gvp_id=f"V_pg_{i:02d}", name=f"Volcano {i:02d}"))
    await db_session.commit()

    response = await client.get("/api/v1/volcanoes?limit=3&offset=0")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 3

    response2 = await client.get("/api/v1/volcanoes?limit=3&offset=3")
    assert len(response2.json()["data"]) == 2


@pytest.mark.asyncio
@pytest.mark.unit
async def test_list_volcanoes_ordered_by_name(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    db_session.add(_make_volcano(gvp_id="V_z", name="Zebra Volcano"))
    db_session.add(_make_volcano(gvp_id="V_a", name="Alpha Volcano"))
    await db_session.commit()

    response = await client.get("/api/v1/volcanoes")
    names = [v["name"] for v in response.json()["data"]]
    assert names == sorted(names)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_volcano_by_id(client: AsyncClient, db_session: AsyncSession) -> None:
    vol = _make_volcano()
    db_session.add(vol)
    await db_session.flush()
    vol_id = vol.id
    await db_session.commit()

    response = await client.get(f"/api/v1/volcanoes/{vol_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Mount Test"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_volcano_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/volcanoes/99999")
    assert response.status_code == 404
