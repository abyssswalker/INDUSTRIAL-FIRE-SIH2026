from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OSMFeature(Base):
    __tablename__ = "osm_features"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    osm_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    osm_type: Mapped[str] = mapped_column(String(20), nullable=False)

    feature_type: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    operator_name: Mapped[str | None] = mapped_column(Text)

    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6), nullable=False)

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="OpenStreetMap",
    )
    tags: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    nearest_clusters: Mapped[list["Cluster"]] = relationship(
        back_populates="nearest_osm_feature",
        foreign_keys="Cluster.nearest_osm_feature_id",
    )

    __table_args__ = (
        UniqueConstraint(
            "osm_id",
            "osm_type",
            name="osm_unique_object",
        ),
        CheckConstraint(
            "osm_type IN ('node', 'way', 'relation')",
            name="osm_type_check",
        ),
        CheckConstraint(
            "latitude BETWEEN -90 AND 90",
            name="osm_latitude_check",
        ),
        CheckConstraint(
            "longitude BETWEEN -180 AND 180",
            name="osm_longitude_check",
        ),
        Index("osm_features_type_idx", "feature_type"),
        Index("osm_features_coordinates_idx", "latitude", "longitude"),
    )


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    center_lat: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
    )
    center_lon: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
    )

    first_detected: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    last_detected: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    recurrence_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    frp_avg: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    frp_variance: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    day_night_ratio: Mapped[Decimal | None] = mapped_column(Numeric(6, 5))

    nearest_osm_feature_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("osm_features.id", ondelete="SET NULL"),
    )
    distance_to_osm_m: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3)
    )

    classification: Mapped[str | None] = mapped_column(String(100))
    classification_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 5)
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
    )
    model_version: Mapped[str | None] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    nearest_osm_feature: Mapped[OSMFeature | None] = relationship(
        back_populates="nearest_clusters",
        foreign_keys=[nearest_osm_feature_id],
    )

    hotspots: Mapped[list["Hotspot"]] = relationship(
        back_populates="cluster",
    )

    __table_args__ = (
        CheckConstraint(
            "center_lat BETWEEN -90 AND 90",
            name="clusters_latitude_check",
        ),
        CheckConstraint(
            "center_lon BETWEEN -180 AND 180",
            name="clusters_longitude_check",
        ),
        CheckConstraint(
            "recurrence_count >= 1",
            name="clusters_recurrence_check",
        ),
        CheckConstraint(
            "day_night_ratio IS NULL OR "
            "day_night_ratio BETWEEN 0 AND 1",
            name="clusters_ratio_check",
        ),
        CheckConstraint(
            "classification_confidence IS NULL OR "
            "classification_confidence BETWEEN 0 AND 1",
            name="clusters_confidence_check",
        ),
        CheckConstraint(
            "status IN ('active', 'resolved', 'under_review')",
            name="clusters_status_check",
        ),
        CheckConstraint(
            "last_detected >= first_detected",
            name="clusters_date_check",
        ),
        Index("clusters_last_detected_idx", "last_detected"),
        Index("clusters_classification_idx", "classification"),
        Index("clusters_status_idx", "status"),
        Index("clusters_coordinates_idx", "center_lat", "center_lon"),
    )


class Hotspot(Base):
    __tablename__ = "hotspots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    firms_id: Mapped[str | None] = mapped_column(Text)

    latitude: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
    )
    longitude: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    acq_date: Mapped[date | None] = mapped_column(Date)
    acq_time: Mapped[time | None] = mapped_column(Time)

    satellite: Mapped[str | None] = mapped_column(String(50))
    instrument: Mapped[str | None] = mapped_column(String(20))
    source: Mapped[str | None] = mapped_column(String(100))

    frp: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    confidence: Mapped[str | None] = mapped_column(String(10))
    day_night: Mapped[str | None] = mapped_column(String(1))

    brightness_ti4: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3)
    )
    brightness_ti5: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3)
    )

    cluster_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("clusters.id", ondelete="SET NULL"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    cluster: Mapped[Cluster | None] = relationship(
        back_populates="hotspots",
    )

    __table_args__ = (
        CheckConstraint(
            "latitude BETWEEN -90 AND 90",
            name="hotspots_latitude_check",
        ),
        CheckConstraint(
            "longitude BETWEEN -180 AND 180",
            name="hotspots_longitude_check",
        ),
        CheckConstraint(
            "confidence IS NULL OR confidence IN "
            "('l', 'n', 'h', 'low', 'nominal', 'high')",
            name="hotspots_confidence_check",
        ),
        CheckConstraint(
            "day_night IS NULL OR day_night IN ('D', 'N')",
            name="hotspots_day_night_check",
        ),
        CheckConstraint(
            "frp IS NULL OR frp >= 0",
            name="hotspots_frp_check",
        ),
        Index("hotspots_detected_at_idx", "detected_at"),
        Index("hotspots_confidence_idx", "confidence"),
        Index("hotspots_cluster_id_idx", "cluster_id"),
        Index("hotspots_coordinates_idx", "latitude", "longitude"),
    )