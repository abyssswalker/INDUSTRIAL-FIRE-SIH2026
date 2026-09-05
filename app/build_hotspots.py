from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sqlalchemy import text

from app.config import (
    DBSCAN_EPS_METERS,
    DBSCAN_MIN_SAMPLES,
    OSM_MATCH_DISTANCE_METERS,
)
from app.database import SessionLocal


EARTH_RADIUS_METERS = 6_371_000


def haversine_distance_m(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    lat_a = math.radians(latitude_a)
    lat_b = math.radians(latitude_b)

    delta_lat = math.radians(
        latitude_b - latitude_a
    )

    delta_lon = math.radians(
        longitude_b - longitude_a
    )

    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_a)
        * math.cos(lat_b)
        * math.sin(delta_lon / 2) ** 2
    )

    return (
        2
        * EARTH_RADIUS_METERS
        * math.asin(math.sqrt(value))
    )


def load_detections() -> pd.DataFrame:
    query = text(
        """
        SELECT
            id,
            latitude,
            longitude,
            detected_at,
            frp,
            day_night
        FROM firms_detections
        ORDER BY detected_at
        """
    )

    with SessionLocal() as db:
        rows = db.execute(query).mappings().all()

    dataframe = pd.DataFrame(rows)

    if dataframe.empty:
        raise RuntimeError(
            "No FIRMS detections are available."
        )

    dataframe["latitude"] = dataframe[
        "latitude"
    ].astype(float)

    dataframe["longitude"] = dataframe[
        "longitude"
    ].astype(float)

    dataframe["detected_at"] = pd.to_datetime(
        dataframe["detected_at"],
        utc=True,
    )

    dataframe["frp"] = pd.to_numeric(
        dataframe["frp"],
        errors="coerce",
    )

    return dataframe


def load_osm_features() -> pd.DataFrame:
    query = text(
        """
        SELECT
            osm_id,
            name,
            feature_type,
            latitude,
            longitude
        FROM osm_features
        """
    )

    with SessionLocal() as db:
        rows = db.execute(query).mappings().all()

    return pd.DataFrame(rows)


def calculate_months_active(
    first_seen: pd.Timestamp,
    last_seen: pd.Timestamp,
) -> float:
    seconds = (
        last_seen - first_seen
    ).total_seconds()

    return max(
        seconds / (30.4375 * 24 * 60 * 60),
        0.0,
    )


def classify_cluster(
    nearest_osm_distance_m: float | None,
    day_count: int,
    night_count: int,
    detection_count: int,
) -> str:
    if (
        nearest_osm_distance_m is not None
        and nearest_osm_distance_m <= 1000
        and detection_count >= 3
    ):
        return "industrial"

    if (
        nearest_osm_distance_m is None
        or nearest_osm_distance_m > 5000
    ):
        if day_count >= night_count:
            return "wildfire"

    return "uncertain"


def find_nearest_osm_feature(
    latitude: float,
    longitude: float,
    osm_features: pd.DataFrame,
):
    if osm_features.empty:
        return None

    nearest = None
    nearest_distance = None

    for _, feature in osm_features.iterrows():
        distance = haversine_distance_m(
            latitude,
            longitude,
            float(feature["latitude"]),
            float(feature["longitude"]),
        )

        if (
            nearest_distance is None
            or distance < nearest_distance
        ):
            nearest = feature
            nearest_distance = distance

    if (
        nearest_distance is None
        or nearest_distance > OSM_MATCH_DISTANCE_METERS
    ):
        return None

    return {
        "osm_id": nearest["osm_id"],
        "name": nearest["name"],
        "feature_type": nearest["feature_type"],
        "distance_m": nearest_distance,
    }


def upsert_hotspot(
    cluster_id: int,
    cluster: pd.DataFrame,
    osm_features: pd.DataFrame,
) -> None:
    centroid_lat = float(
        cluster["latitude"].mean()
    )

    centroid_lon = float(
        cluster["longitude"].mean()
    )

    detection_count = len(cluster)

    first_seen = cluster["detected_at"].min()
    last_seen = cluster["detected_at"].max()

    months_active = calculate_months_active(
        first_seen,
        last_seen,
    )

    recurrence_rate = (
        detection_count / months_active
        if months_active > 0
        else float(detection_count)
    )

    frp_values = cluster["frp"].dropna()

    frp_mean = (
        float(frp_values.mean())
        if not frp_values.empty
        else None
    )

    frp_std = (
        float(frp_values.std(ddof=0))
        if not frp_values.empty
        else None
    )

    frp_cv = (
        frp_std / frp_mean
        if frp_mean and frp_std is not None
        else None
    )

    day_count = int(
        (cluster["day_night"] == "D").sum()
    )

    night_count = int(
        (cluster["day_night"] == "N").sum()
    )

    daynight_ratio = (
        day_count / detection_count
        if detection_count > 0
        else None
    )

    nearest_osm = find_nearest_osm_feature(
        centroid_lat,
        centroid_lon,
        osm_features,
    )

    nearest_distance = (
        nearest_osm["distance_m"]
        if nearest_osm
        else None
    )

    classification = classify_cluster(
        nearest_distance,
        day_count,
        night_count,
        detection_count,
    )

    nearest_osm_id = (
        nearest_osm["osm_id"]
        if nearest_osm
        else None
    )

    nearest_name = (
        nearest_osm["name"]
        if nearest_osm
        else None
    )

    nearest_type = (
        nearest_osm["feature_type"]
        if nearest_osm
        else None
    )

    statement = text(
        """
        INSERT INTO hotspots (
            cluster_id,
            centroid_lat,
            centroid_lon,
            geom,
            detection_count,
            first_seen,
            last_seen,
            months_active,
            recurrence_rate,
            frp_mean,
            frp_std,
            frp_cv,
            day_count,
            night_count,
            daynight_ratio,
            nearest_osm_id,
            nearest_industrial_distance_m,
            nearest_industrial_type,
            nearest_industrial_name,
            classification,
            confidence,
            classifier_version,
            updated_at
        )
        VALUES (
            :cluster_id,
            :centroid_lat,
            :centroid_lon,
            ST_SetSRID(
                ST_MakePoint(
                    :centroid_lon,
                    :centroid_lat
                ),
                4326
            )::geography,
            :detection_count,
            :first_seen,
            :last_seen,
            :months_active,
            :recurrence_rate,
            :frp_mean,
            :frp_std,
            :frp_cv,
            :day_count,
            :night_count,
            :daynight_ratio,
            :nearest_osm_id,
            :nearest_distance,
            :nearest_type,
            :nearest_name,
            :classification,
            NULL,
            'rule-v1',
            CURRENT_TIMESTAMP
        )
        ON CONFLICT (cluster_id)
        DO UPDATE SET
            centroid_lat = EXCLUDED.centroid_lat,
            centroid_lon = EXCLUDED.centroid_lon,
            geom = EXCLUDED.geom,
            detection_count = EXCLUDED.detection_count,
            first_seen = EXCLUDED.first_seen,
            last_seen = EXCLUDED.last_seen,
            months_active = EXCLUDED.months_active,
            recurrence_rate = EXCLUDED.recurrence_rate,
            frp_mean = EXCLUDED.frp_mean,
            frp_std = EXCLUDED.frp_std,
            frp_cv = EXCLUDED.frp_cv,
            day_count = EXCLUDED.day_count,
            night_count = EXCLUDED.night_count,
            daynight_ratio = EXCLUDED.daynight_ratio,
            nearest_osm_id = EXCLUDED.nearest_osm_id,
            nearest_industrial_distance_m =
                EXCLUDED.nearest_industrial_distance_m,
            nearest_industrial_type =
                EXCLUDED.nearest_industrial_type,
            nearest_industrial_name =
                EXCLUDED.nearest_industrial_name,
            classification = EXCLUDED.classification,
            classifier_version =
                EXCLUDED.classifier_version,
            updated_at = CURRENT_TIMESTAMP
        """
    )

    parameters = {
        "cluster_id": cluster_id,
        "centroid_lat": centroid_lat,
        "centroid_lon": centroid_lon,
        "detection_count": detection_count,
        "first_seen": first_seen.to_pydatetime(),
        "last_seen": last_seen.to_pydatetime(),
        "months_active": months_active,
        "recurrence_rate": recurrence_rate,
        "frp_mean": frp_mean,
        "frp_std": frp_std,
        "frp_cv": frp_cv,
        "day_count": day_count,
        "night_count": night_count,
        "daynight_ratio": daynight_ratio,
        "nearest_osm_id": nearest_osm_id,
        "nearest_distance": nearest_distance,
        "nearest_type": nearest_type,
        "nearest_name": nearest_name,
        "classification": classification,
    }

    with SessionLocal() as db:
        db.execute(statement, parameters)
        db.commit()


def build_hotspots() -> int:
    detections = load_detections()
    osm_features = load_osm_features()

    coordinates = np.radians(
        detections[
            ["latitude", "longitude"]
        ].to_numpy()
    )

    eps_radians = (
        DBSCAN_EPS_METERS / EARTH_RADIUS_METERS
    )

    model = DBSCAN(
        eps=eps_radians,
        min_samples=DBSCAN_MIN_SAMPLES,
        metric="haversine",
    )

    detections["cluster_label"] = model.fit_predict(
        coordinates
    )

    detections = detections[
        detections["cluster_label"] >= 0
    ].copy()

    if detections.empty:
        raise RuntimeError(
            "DBSCAN found no valid clusters."
        )

    unique_labels = sorted(
        detections["cluster_label"].unique()
    )

    for index, label in enumerate(unique_labels, start=1):
        cluster = detections[
            detections["cluster_label"] == label
        ].copy()

        upsert_hotspot(
            cluster_id=index,
            cluster=cluster,
            osm_features=osm_features,
        )

        update_cluster_ids(
            index,
            cluster,
        )

    return len(unique_labels)


def update_cluster_ids(
    cluster_id: int,
    cluster: pd.DataFrame,
) -> None:
    detection_ids = [
        int(value)
        for value in cluster["id"].tolist()
    ]

    statement = text(
        """
        UPDATE firms_detections
        SET cluster_id = :cluster_id
        WHERE id = ANY(:detection_ids)
        """
    )

    with SessionLocal() as db:
        db.execute(
            statement,
            {
                "cluster_id": cluster_id,
                "detection_ids": detection_ids,
            },
        )
        db.commit()


if __name__ == "__main__":
    count = build_hotspots()

    print(
        f"Created or updated {count} hotspot clusters."
    )