from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import FIRMSDetection, Hotspot, OSMFeature
from app.schemas import (
    HotspotCreate,
    OSMFeatureCreate,
)


def create_osm_feature(
    db: Session,
    data: OSMFeatureCreate,
) -> OSMFeature:
    feature = OSMFeature(
        osm_id=data.osm_id,
        name=data.name,
        feature_type=data.feature_type,
        latitude=data.latitude,
        longitude=data.longitude,
        properties=data.properties,
        source=data.source,
    )

    db.add(feature)
    db.commit()
    db.refresh(feature)

    return feature


def create_hotspot(
    db: Session,
    data: HotspotCreate,
) -> Hotspot:
    hotspot = Hotspot(
        cluster_id=data.cluster_id,
        centroid_lat=data.centroid_lat,
        centroid_lon=data.centroid_lon,
        detection_count=data.detection_count,
        first_seen=data.first_seen,
        last_seen=data.last_seen,
        months_active=data.months_active,
        recurrence_rate=data.recurrence_rate,
        frp_mean=data.frp_mean,
        frp_std=data.frp_std,
        frp_cv=data.frp_cv,
        day_count=data.day_count,
        night_count=data.night_count,
        daynight_ratio=data.daynight_ratio,
        nearest_osm_id=data.nearest_osm_id,
        nearest_industrial_distance_m=(
            data.nearest_industrial_distance_m
        ),
        nearest_industrial_type=data.nearest_industrial_type,
        nearest_industrial_name=data.nearest_industrial_name,
        classification=data.classification,
        confidence=data.confidence,
        classifier_version=data.classifier_version,
    )

    db.add(hotspot)
    db.commit()
    db.refresh(hotspot)

    return hotspot


def get_all_hotspots(
    db: Session,
    limit: int = 100,
) -> list[Hotspot]:
    statement = (
        select(Hotspot)
        .options(joinedload(Hotspot.nearest_osm_feature))
        .order_by(Hotspot.last_seen.desc())
        .limit(limit)
    )

    return list(db.scalars(statement).unique().all())


def get_hotspots_by_classification(
    db: Session,
    classification: str,
) -> list[Hotspot]:
    statement = (
        select(Hotspot)
        .where(Hotspot.classification == classification)
        .order_by(Hotspot.last_seen.desc())
    )

    return list(db.scalars(statement).all())


def get_uncertain_hotspots(
    db: Session,
) -> list[Hotspot]:
    return get_hotspots_by_classification(db, "uncertain")


def get_industrial_hotspots(
    db: Session,
) -> list[Hotspot]:
    return get_hotspots_by_classification(db, "industrial")


def get_wildfire_hotspots(
    db: Session,
) -> list[Hotspot]:
    return get_hotspots_by_classification(db, "wildfire")


def get_hotspot(
    db: Session,
    cluster_id: int,
) -> Hotspot | None:
    statement = (
        select(Hotspot)
        .options(
            joinedload(Hotspot.nearest_osm_feature),
            joinedload(Hotspot.firms_detections),
        )
        .where(Hotspot.cluster_id == cluster_id)
    )

    return db.scalars(statement).unique().first()


def get_nearest_osm_feature_basic(
    db: Session,
    latitude: float,
    longitude: float,
) -> OSMFeature | None:
    """
    Temporary non-spatial version.

    It calculates approximate coordinate distance in Python.
    Replace it with PostGIS when spatial support is added.
    """
    statement = select(OSMFeature)
    features = list(db.scalars(statement).all())

    if not features:
        return None

    def distance(feature: OSMFeature) -> float:
        lat_diff = float(feature.latitude) - latitude
        lon_diff = float(feature.longitude) - longitude
        return lat_diff**2 + lon_diff**2

    return min(features, key=distance)


def update_osm_join_fields(
    db: Session,
    cluster_id: int,
    osm_id: str,
    distance_m: float,
) -> Hotspot | None:
    """
    Used by the Java matcher after it finds the nearest OSM feature.

    The name and type are copied from osm_features instead of
    trusting a separate CSV field.
    """
    hotspot = db.get(Hotspot, cluster_id)
    feature = db.scalar(
        select(OSMFeature).where(OSMFeature.osm_id == osm_id)
    )

    if hotspot is None or feature is None:
        return None

    hotspot.nearest_osm_id = feature.osm_id
    hotspot.nearest_industrial_name = feature.name
    hotspot.nearest_industrial_type = feature.feature_type
    hotspot.nearest_industrial_distance_m = distance_m

    db.commit()
    db.refresh(hotspot)

    return hotspot