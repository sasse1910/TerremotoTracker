from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Earthquake(Base):
    __tablename__ = "earthquakes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usgs_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    magnitude: Mapped[float] = mapped_column(Float, nullable=False)
    magnitude_type: Mapped[str | None] = mapped_column(String(10))

    place: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    updated_at_usgs: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    depth_km: Mapped[float | None] = mapped_column(Float)

    status: Mapped[str | None] = mapped_column(String(20))
    tsunami: Mapped[int] = mapped_column(Integer, default=0)
    alert: Mapped[str | None] = mapped_column(String(10))
    url: Mapped[str | None] = mapped_column(String(500))
    detail_url: Mapped[str | None] = mapped_column(String(500))

    created_in_db: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_earthquake_mag_time", "magnitude", "occurred_at"),
        Index("ix_earthquake_geo", "latitude", "longitude"),
    )

    def __repr__(self) -> str:
        return f"<Earthquake {self.usgs_id} M{self.magnitude} @ {self.place}>"
