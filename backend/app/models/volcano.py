from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Volcano(Base):
    __tablename__ = "volcanoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gvp_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str | None] = mapped_column(String(100))
    region: Mapped[str | None] = mapped_column(String(100))
    subregion: Mapped[str | None] = mapped_column(String(100))

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    elevation_m: Mapped[int | None] = mapped_column(Integer)

    volcano_type: Mapped[str | None] = mapped_column(String(100))
    last_eruption_year: Mapped[int | None] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    activity_level: Mapped[str | None] = mapped_column(String(50))

    description: Mapped[str | None] = mapped_column(Text)
    wikipedia_url: Mapped[str | None] = mapped_column(String(500))

    created_in_db: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<Volcano {self.gvp_id} '{self.name}' @ {self.country}>"
