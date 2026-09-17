from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict


class LiveFirePoint(BaseModel):
    latitude: float
    longitude: float
    frp: float
    confidence: Literal["l", "n", "h"]
    DayNight: Literal["D", "N"]


class LiveInferenceRequest(BaseModel):
    points: list[LiveFirePoint]

class HotspotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cluster_id: int
    centroid_lat: Decimal
    centroid_lon: Decimal
    detection_count: int
    first_seen: datetime
    last_seen: datetime
    months_active: Decimal | None
    recurrence_rate: Decimal | None
    frp_mean: Decimal | None
    frp_std: Decimal | None
    frp_cv: Decimal | None
    day_count: int
    night_count: int
    daynight_ratio: Decimal | None
    nearest_osm_id: str | None
    nearest_industrial_distance_m: Decimal | None
    nearest_industrial_type: str | None
    nearest_industrial_name: str | None
    classification: str
    confidence: Decimal | None
    classifier_version: str | None