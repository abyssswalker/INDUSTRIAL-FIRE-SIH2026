from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import BigInteger, Integer, Numeric, String, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, declarative_base

Base = declarative_base()

class Fire(Base):
    __tablename__ = "fires"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    firms_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    frp: Mapped[Optional[float]] = mapped_column(Numeric(12, 4))
    acq_timestamptz: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    geom: Mapped[Geometry] = mapped_column(Geometry("POINT", srid=4326), nullable=False)

class IndustrialArea(Base):
    __tablename__ = "industrial_areas"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(Text)
    feature_type: Mapped[Optional[str]] = mapped_column(Text)
    properties: Mapped[Optional[dict]] = mapped_column(String)  # or JSONB if you configure it
    geom: Mapped[Geometry] = mapped_column(Geometry("POLYGON", srid=4326), nullable=False)

class ClusterBaseline(Base):
    __tablename__ = "cluster_baselines"

    cluster_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    centroid_geom: Mapped[Optional[Geometry]] = mapped_column(Geometry("POINT", srid=4326))
    frp_mean: Mapped[Optional[float]] = mapped_column(Numeric(12, 4))
    frp_std: Mapped[Optional[float]] = mapped_column(Numeric(12, 4))
    detection_count: Mapped[Optional[int]] = mapped_column(Integer)
    label: Mapped[Optional[str]] = mapped_column(Text)
    industrial_score: Mapped[Optional[float]] = mapped_column(Numeric(12, 6))
    wildfire_score: Mapped[Optional[float]] = mapped_column(Numeric(12, 6))
    recurrence_rate: Mapped[Optional[float]] = mapped_column(Numeric(12, 8))
    nearest_industrial_distance_m: Mapped[Optional[float]] = mapped_column(Numeric(18, 6))
    nearest_industrial_type: Mapped[Optional[str]] = mapped_column(Text)
