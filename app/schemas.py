from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Classification = Literal[
    "industrial",
    "wildfire",
    "uncertain",
]


class OSMFeatureCreate(BaseModel):
    osm_id: str
    name: str | None = None
    feature_type: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    properties: dict | None = None
    source: str = "OpenStreetMap"


class OSMFeatureResponse(OSMFeatureCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HotspotCreate(BaseModel):
    cluster_id: int
    centroid_lat: float = Field(ge=-90, le=90)
    centroid_lon: float = Field(ge=-180, le=180)

    detection_count: int = Field(ge=0)

    first_seen: datetime
    last_seen: datetime

    months_active: float | None = Field(default=None, ge=0)
    recurrence_rate: float | None = Field(default=None, ge=0)

    frp_mean: float | None = Field(default=None, ge=0)
    frp_std: float | None = Field(default=None, ge=0)
    frp_cv: float | None = Field(default=None, ge=0)

    day_count: int = Field(default=0, ge=0)
    night_count: int = Field(default=0, ge=0)
    daynight_ratio: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    nearest_osm_id: str | None = None
    nearest_industrial_distance_m: float | None = Field(
        default=None,
        ge=0,
    )
    nearest_industrial_type: str | None = None
    nearest_industrial_name: str | None = None

    classification: Classification = "uncertain"

    # NULL is allowed until XGBoost is implemented
    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    classifier_version: str | None = None


class HotspotResponse(HotspotCreate):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)