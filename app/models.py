from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OSMFeature(Base):
    __tablename__ = "osm_features"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    osm_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )

    name: Mapped[str | None] = mapped_column(Text)

    feature_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    latitude: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
    )

    longitude: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
    )

    properties: Mapped[dict[str, Any] | None] = mapped_column(
        JSON
    )

    source: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="OpenStreetMap",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
    )

    hotspots: Mapped[list["Hotspot"]] = relationship(
        back_populates="nearest_osm_feature"
    )

    __table_args__ = (
        CheckConstraint(
            "latitude BETWEEN -90 AND 90",
            name="osm_latitude_check",
        ),
        CheckConstraint(
            "longitude BETWEEN -180 AND 180",
            name="osm_longitude_check",
        ),
        Index(
            "osm_features_type_idx",
            "feature_type",
        ),
    )


class Hotspot(Base):
    __tablename__ = "hotspots"

    cluster_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    centroid_lat: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
    )

    centroid_lon: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
    )

    detection_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    months_active: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4)
    )

    recurrence_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4)
    )

    frp_mean: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4)
    )

    frp_std: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4)
    )

    frp_cv: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6)
    )

    day_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    night_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    daynight_ratio: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6)
    )

    nearest_osm_id: Mapped[str | None] = mapped_column(
        Text,
        ForeignKey(
            "osm_features.osm_id",
            ondelete="SET NULL",
        ),
    )

    nearest_industrial_distance_m: Mapped[
        Decimal | None
    ] = mapped_column(Numeric(14, 4))

    nearest_industrial_type: Mapped[
        str | None
    ] = mapped_column(Text)

    nearest_industrial_name: Mapped[
        str | None
    ] = mapped_column(Text)

    classification: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="uncertain",
    )

    confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 5)
    )

    classifier_version: Mapped[
        str | None
    ] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
    )

    nearest_osm_feature: Mapped[
        OSMFeature | None
    ] = relationship(
        back_populates="hotspots"
    )

    firms_detections: Mapped[
        list["FIRMSDetection"]
    ] = relationship(
        back_populates="hotspot"
    )

    __table_args__ = (
        CheckConstraint(
            "classification IN "
            "('industrial', 'wildfire', 'uncertain')",
            name="hotspots_classification_check",
        ),
        CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="hotspots_confidence_check",
        ),
        Index(
            "hotspots_classification_idx",
            "classification",
        ),
    )


class FIRMSDetection(Base):
    __tablename__ = "firms_detections"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    firms_id: Mapped[str | None] = mapped_column(
        Text,
        unique=True,
    )

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

    acq_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    satellite: Mapped[str | None] = mapped_column(Text)

    instrument: Mapped[str | None] = mapped_column(Text)

    source: Mapped[str | None] = mapped_column(Text)

    frp: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4)
    )

    confidence: Mapped[str | None] = mapped_column(Text)

    day_night: Mapped[str | None] = mapped_column(Text)

    brightness_ti4: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4)
    )

    brightness_ti5: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4)
    )

    cluster_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "hotspots.cluster_id",
            ondelete="SET NULL",
        ),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
    )

    hotspot: Mapped[
        Hotspot | None
    ] = relationship(
        back_populates="firms_detections"
    )

    __table_args__ = (
        CheckConstraint(
            "day_night IS NULL OR day_night IN ('D', 'N')",
            name="firms_daynight_check",
        ),
        Index(
            "firms_detected_at_idx",
            "detected_at",
        ),
    )