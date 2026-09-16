from __future__ import annotations

import math
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sqlalchemy import text
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.config import DBSCAN_EPS_METERS, DBSCAN_MIN_SAMPLES, OSM_MATCH_DISTANCE_METERS
from app.database import SessionLocal
from app.models import Hotspot

EARTH_RADIUS_METERS = 6_371_000

def haversine_distance_m(lat_a, lon_a, lat_b, lon_b):
    lat_a = math.radians(lat_a)
    lat_b = math.radians(lat_b)
    dlat = math.radians(lat_b - lat_a)
    dlon = math.radians(lon_b - lon_a)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat_a) * math.cos(lat_b) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_METERS * math.asin(math.sqrt(a))

def load_detections() -> pd.DataFrame:
    with SessionLocal() as db:
        rows = db.execute(
            text("SELECT id, latitude, longitude, detected_at, frp, day_night FROM firms_detections ORDER BY detected_at")
        ).mappings().all()
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("No FIRMS detections are available.")
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    df["detected_at"] = pd.to_datetime(df["detected_at"], utc=True)
    df["frp"] = pd.to_numeric(df["frp"], errors="coerce")
    return df

def load_osm_features() -> pd.DataFrame:
    with SessionLocal() as db:
        rows = db.execute(
            text("SELECT osm_id, name, feature_type, latitude, longitude FROM osm_features")
        ).mappings().all()
    return pd.DataFrame(rows)

def calculate_months_active(first_seen, last_seen):
    return max((last_seen - first_seen).total_seconds() / (30.4375 * 24 * 3600), 0.0)

def classify_cluster(nearest_distance_m, day_count, night_count, detection_count):
    if nearest_distance_m is not None and nearest_distance_m <= 1000 and detection_count >= 3:
        return "industrial"
    if nearest_distance_m is None or nearest_distance_m > 5000:
        if day_count >= night_count:
            return "wildfire"
    return "uncertain"

def find_nearest_osm_feature(lat, lon, osm_features):
    if osm_features.empty:
        return None
    nearest = None
    nearest_distance = None
    for _, feature in osm_features.iterrows():
        distance = haversine_distance_m(lat, lon, float(feature["latitude"]), float(feature["longitude"]))
        if nearest_distance is None or distance < nearest_distance:
            nearest = feature
            nearest_distance = distance
    if nearest_distance is None or nearest_distance > OSM_MATCH_DISTANCE_METERS:
        return None
    return {
        "osm_id": nearest["osm_id"],
        "name": nearest["name"],
        "feature_type": nearest["feature_type"],
        "distance_m": nearest_distance,
    }

def build_hotspots() -> int:
    detections = load_detections()
    osm_features = load_osm_features()

    coords = np.radians(detections[["latitude", "longitude"]].to_numpy())
    eps_radians = DBSCAN_EPS_METERS / EARTH_RADIUS_METERS
    model = DBSCAN(eps=eps_radians, min_samples=DBSCAN_MIN_SAMPLES, metric="haversine")
    detections["cluster_label"] = model.fit_predict(coords)
    detections = detections[detections["cluster_label"] >= 0].copy()

    if detections.empty:
        raise RuntimeError("DBSCAN found no valid clusters.")

    with SessionLocal() as db:
        for new_cluster_id, label in enumerate(sorted(detections["cluster_label"].unique()), start=1):
            cluster = detections[detections["cluster_label"] == label].copy()
            centroid_lat = float(cluster["latitude"].mean())
            centroid_lon = float(cluster["longitude"].mean())
            detection_count = len(cluster)
            first_seen = cluster["detected_at"].min().to_pydatetime()
            last_seen = cluster["detected_at"].max().to_pydatetime()
            months_active = calculate_months_active(first_seen, last_seen)
            recurrence_rate = detection_count / months_active if months_active > 0 else float(detection_count)

            frp_values = cluster["frp"].dropna()
            frp_mean = float(frp_values.mean()) if not frp_values.empty else None
            frp_std = float(frp_values.std(ddof=0)) if not frp_values.empty else None
            frp_cv = (frp_std / frp_mean) if frp_mean and frp_std is not None else None

            day_count = int((cluster["day_night"] == "D").sum())
            night_count = int((cluster["day_night"] == "N").sum())
            daynight_ratio = day_count / detection_count if detection_count > 0 else None

            nearest_osm = find_nearest_osm_feature(centroid_lat, centroid_lon, osm_features)
            nearest_distance = nearest_osm["distance_m"] if nearest_osm else None
            classification = classify_cluster(nearest_distance, day_count, night_count, detection_count)

            stmt = sqlite_insert(Hotspot).values(
                cluster_id=new_cluster_id,
                centroid_lat=centroid_lat,
                centroid_lon=centroid_lon,
                detection_count=detection_count,
                first_seen=first_seen,
                last_seen=last_seen,
                months_active=months_active,
                recurrence_rate=recurrence_rate,
                frp_mean=frp_mean,
                frp_std=frp_std,
                frp_cv=frp_cv,
                day_count=day_count,
                night_count=night_count,
                daynight_ratio=daynight_ratio,
                nearest_osm_id=nearest_osm["osm_id"] if nearest_osm else None,
                nearest_industrial_distance_m=nearest_distance,
                nearest_industrial_type=nearest_osm["feature_type"] if nearest_osm else None,
                nearest_industrial_name=nearest_osm["name"] if nearest_osm else None,
                classification=classification,
                confidence=None,
                classifier_version="rule-v1",
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["cluster_id"],
                set_={
                    "centroid_lat": stmt.excluded.centroid_lat,
                    "centroid_lon": stmt.excluded.centroid_lon,
                    "detection_count": stmt.excluded.detection_count,
                    "first_seen": stmt.excluded.first_seen,
                    "last_seen": stmt.excluded.last_seen,
                    "months_active": stmt.excluded.months_active,
                    "recurrence_rate": stmt.excluded.recurrence_rate,
                    "frp_mean": stmt.excluded.frp_mean,
                    "frp_std": stmt.excluded.frp_std,
                    "frp_cv": stmt.excluded.frp_cv,
                    "day_count": stmt.excluded.day_count,
                    "night_count": stmt.excluded.night_count,
                    "daynight_ratio": stmt.excluded.daynight_ratio,
                    "nearest_osm_id": stmt.excluded.nearest_osm_id,
                    "nearest_industrial_distance_m": stmt.excluded.nearest_industrial_distance_m,
                    "nearest_industrial_type": stmt.excluded.nearest_industrial_type,
                    "nearest_industrial_name": stmt.excluded.nearest_industrial_name,
                    "classification": stmt.excluded.classification,
                    "classifier_version": stmt.excluded.classifier_version,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            db.execute(stmt)
            db.execute(
                text("UPDATE firms_detections SET cluster_id = :cid WHERE id = :did"),
                [{"cid": new_cluster_id, "did": int(row_id)} for row_id in cluster["id"].tolist()],
            )
        db.commit()

    return len(sorted(detections["cluster_label"].unique()))

if __name__ == "__main__":
    print(f"Created or updated {build_hotspots()} hotspot clusters.")