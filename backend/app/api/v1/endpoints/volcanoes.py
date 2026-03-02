from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.volcano import Volcano
from app.schemas.volcano import VolcanoListResponse, VolcanoOut

router = APIRouter()


@router.get("", response_model=VolcanoListResponse)
async def list_volcanoes(
    is_active: bool | None = Query(default=None),
    country: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> VolcanoListResponse:
    stmt = select(Volcano)

    if is_active is not None:
        stmt = stmt.where(Volcano.is_active == is_active)
    if country is not None:
        stmt = stmt.where(Volcano.country.ilike(f"%{country}%"))

    stmt = stmt.order_by(Volcano.name)

    result = await db.execute(stmt.offset(offset).limit(limit))
    volcanoes = result.scalars().all()

    return VolcanoListResponse(count=len(volcanoes), data=list(volcanoes))


@router.get("/{volcano_id}", response_model=VolcanoOut)
async def get_volcano(
    volcano_id: int,
    db: AsyncSession = Depends(get_db),
) -> VolcanoOut:
    result = await db.execute(select(Volcano).where(Volcano.id == volcano_id))
    vol = result.scalar_one_or_none()
    if vol is None:
        raise HTTPException(status_code=404, detail="Volcano not found")
    return vol
