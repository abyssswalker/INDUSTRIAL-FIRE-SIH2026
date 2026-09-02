from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Cluster, Hotspot, OSMFeature
from app.schemas import (
    ClusterCreate,
    HotspotCreate,
    OSMFeatureCreate,
)


def create_hotspot(
    db: Session,
    payload: HotspotCreate,
) -> Hotspot:
    hotspot = Hotspot(
        firms_id=payload.firms_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        detected_at=payload.detected_at,
        acq_date=payload.acq_date,
        acq_time=payload.acq_time,
        satellite=payload.satellite,
        instrument=payload.instrument,
        source=payload.source,
        frp=payload.frp,
        confidence=payload.confidence,
        day_night=payload.day_night,
        brightness_ti4=payload.brightness_ti4,
        brightness_ti5=payload.brightness_ti5,
        cluster_id=payload.cluster_id,
    )

    db.add(hotspot)
    db.commit()
    db.refresh(hotspot)

    return hotspot


def create_cluster(
    db: Session,
    payload: ClusterCreate,
) -> Cluster:
    cluster = Cluster(
        center_lat=payload.center_lat,
        center_lon=payload.center_lon,
        first_detected=payload.first_detected,
        last_detected=payload.last_detected,
        recurrence_count=payload.recurrence_count,
        frp_avg=payload.frp_avg,
        frp_variance=payload.frp_variance,
        day_night_ratio=payload.day_night_ratio,
        nearest_osm_feature_id=payload.nearest_osm_feature_id,
        distance_to_osm_m=payload.distance_to_osm_m,
        classification=payload.classification,
        classification_confidence=payload.classification_confidence,
        status=payload.status,
        model_version=payload.model_version,
    )

    db.add(cluster)
    db.commit()
    db.refresh(cluster)

    return cluster


def create_osm_feature(
    db: Session,
    payload: OSMFeatureCreate,
) -> OSMFeature:
    feature = OSMFeature(
        osm_id=payload.osm_id,
        osm_type=payload.osm_type,
        feature_type=payload.feature_type,
        name=payload.name,
        operator_name=payload.operator_name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        source=payload.source,
        tags=payload.tags,
    )

    db.add(feature)
    db.commit()
    db.refresh(feature)

    return feature


def get_all_hotspots(
    db: Session,
    limit: int = 100,
) -> list[Hotspot]:
    statement = (
        select(Hotspot)
        .order_by(Hotspot.detected_at.desc())
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def get_hotspots_by_date(
    db: Session,
    start_date: datetime,
    end_date: datetime,
) -> list[Hotspot]:
    statement = (
        select(Hotspot)
        .where(
            Hotspot.detected_at >= start_date,
            Hotspot.detected_at < end_date,
        )
        .order_by(Hotspot.detected_at.desc())
    )

    return list(db.scalars(statement).all())


def get_clusters_by_classification(
    db: Session,
    classification: str,
) -> list[Cluster]:
    statement = (
        select(Cluster)
        .where(Cluster.classification == classification)
        .order_by(
            Cluster.classification_confidence.desc().nullslast()
        )
    )

    return list(db.scalars(statement).all())


def get_active_clusters(
    db: Session,
    minimum_confidence: float = 0.70,
) -> list[Cluster]:
    statement = (
        select(Cluster)
        .where(
            Cluster.status == "active",
            Cluster.classification_confidence
            >= minimum_confidence,
        )
        .order_by(Cluster.last_detected.desc())
    )

    return list(db.scalars(statement).all())


def get_cluster_with_hotspots(
    db: Session,
    cluster_id: int,
) -> Cluster | None:
    statement = (
        select(Cluster)
        .options(joinedload(Cluster.hotspots))
        .where(Cluster.id == cluster_id)
    )

    return db.scalars(statement).unique().first()


def get_nearest_osm_feature_python(
    db: Session,
    latitude: float,
    longitude: float,
) -> OSMFeature | None:
    """
    Temporary prototype version.

    It retrieves OSM features and calculates distance in Python.
    Replace this with PostGIS when spatial support is added.
    """
    statement = select(OSMFeature)
    features = list(db.scalars(statement).all())

    if not features:
        return None

    def squared_distance(feature: OSMFeature) -> float:
        lat_diff = float(feature.latitude) - latitude
        lon_diff = float(feature.longitude) - longitude
        return lat_diff**2 + lon_diff**2

    return min(features, key=squared_distance)