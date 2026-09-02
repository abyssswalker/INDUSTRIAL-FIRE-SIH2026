from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class HotspotCreate(BaseModel):
    firms_id: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    detected_at: datetime
    acq_date: date | None = None
    acq_time: time | None = None
    satellite: str | None = None
    instrument: str | None = None
    source: str | None = None
    frp: float | None = Field(default=None, ge=0)
    confidence: str | None = None
    day_night: str | None = None
    brightness_ti4: float | None = None
    brightness_ti5: float | None = None
    cluster_id: int | None = None


class HotspotResponse(HotspotCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClusterCreate(BaseModel):
    center_lat: float = Field(ge=-90, le=90)
    center_lon: float = Field(ge=-180, le=180)
    first_detected: datetime
    last_detected: datetime
    recurrence_count: int = Field(default=1, ge=1)
    frp_avg: float | None = None
    frp_variance: float | None = None
    day_night_ratio: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    nearest_osm_feature_id: int | None = None
    distance_to_osm_m: float | None = Field(default=None, ge=0)
    classification: str | None = None
    classification_confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )
    status: str = "active"
    model_version: str | None = None


class ClusterResponse(ClusterCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OSMFeatureCreate(BaseModel):
    osm_id: int
    osm_type: str
    feature_type: str
    name: str | None = None
    operator_name: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    source: str = "OpenStreetMap"
    tags: dict | None = None


class OSMFeatureResponse(OSMFeatureCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)