from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ClusterSummary(Base):
    __tablename__ = "cluster_summaries"

    cluster_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    detection_count: Mapped[int | None] = mapped_column(Integer)

    first_seen: Mapped[datetime | None] = mapped_column(DateTime)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime)

    centroid_lat: Mapped[Decimal | None] = mapped_column(Numeric(12, 8))
    centroid_lon: Mapped[Decimal | None] = mapped_column(Numeric(12, 8))

    nearest_industrial_distance_m: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    nearest_industrial_type: Mapped[str | None] = mapped_column(Text)

    months_active: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    recurrence_rate: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))

    frp_mean: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    frp_std: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    frp_cv: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))

    day_count: Mapped[int | None] = mapped_column(Integer)
    night_count: Mapped[int | None] = mapped_column(Integer)
    daynight_ratio: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))

    industrial_score: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    wildfire_score: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))

    label: Mapped[str | None] = mapped_column(String(32))