from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import text

from app.database import SessionLocal


def get_osm_id(feature: dict) -> str | None:
    properties = feature.get("properties") or {}

    for key in (
        "id",
        "@id",
        "osm_id",
        "osm3s_id",
    ):
        value = properties.get(key)

        if value:
            return str(value)

    feature_id = feature.get("id")

    if feature_id:
        return str(feature_id)

    return None


def get_feature_name(properties: dict) -> str | None:
    for key in (
        "name",
        "official_name",
        "alt_name",
        "operator",
    ):
        value = properties.get(key)

        if value:
            return str(value)

    return None


def get_feature_type(properties: dict) -> str:
    preferred_tags = [
        "landuse",
        "industrial",
        "power",
        "man_made",
        "building",
        "amenity",
    ]

    for tag in preferred_tags:
        value = properties.get(tag)

        if value:
            return f"{tag}={value}"

    return "osm_feature"


def get_point_coordinates(feature: dict):
    geometry = feature.get("geometry") or {}
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")

    if geometry_type == "Point":
        return (
            float(coordinates[0]),
            float(coordinates[1]),
        )

    if geometry_type == "Polygon":
        ring = coordinates[0]

        longitude = sum(
            point[0] for point in ring
        ) / len(ring)

        latitude = sum(
            point[1] for point in ring
        ) / len(ring)

        return longitude, latitude

    if geometry_type == "MultiPolygon":
        first_polygon = coordinates[0][0]

        longitude = sum(
            point[0] for point in first_polygon
        ) / len(first_polygon)

        latitude = sum(
            point[1] for point in first_polygon
        ) / len(first_polygon)

        return longitude, latitude

    if geometry_type == "LineString":
        longitude = sum(
            point[0] for point in coordinates
        ) / len(coordinates)

        latitude = sum(
            point[1] for point in coordinates
        ) / len(coordinates)

        return longitude, latitude

    return None


def import_osm_geojson(geojson_path: str) -> int:
    path = Path(geojson_path)

    if not path.exists():
        raise FileNotFoundError(
            f"OSM GeoJSON was not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        geojson = json.load(file)

    features = geojson.get("features", [])
    imported = 0

    with SessionLocal() as db:
        for feature in features:
            properties = feature.get("properties") or {}

            osm_id = get_osm_id(feature)
            coordinates = get_point_coordinates(feature)

            if not osm_id or not coordinates:
                continue

            longitude, latitude = coordinates

            name = get_feature_name(properties)
            feature_type = get_feature_type(properties)

            statement = text(
                """
                INSERT INTO osm_features (
                    osm_id,
                    name,
                    feature_type,
                    latitude,
                    longitude,
                    properties,
                    geom,
                    source,
                    updated_at
                )
                VALUES (
                    :osm_id,
                    :name,
                    :feature_type,
                    :latitude,
                    :longitude,
                    CAST(:properties AS jsonb),
                    ST_SetSRID(
                        ST_MakePoint(
                            :longitude,
                            :latitude
                        ),
                        4326
                    )::geography,
                    'OpenStreetMap',
                    CURRENT_TIMESTAMP
                )
                ON CONFLICT (osm_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    feature_type = EXCLUDED.feature_type,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    properties = EXCLUDED.properties,
                    geom = EXCLUDED.geom,
                    updated_at = CURRENT_TIMESTAMP
                """
            )

            db.execute(
                statement,
                {
                    "osm_id": osm_id,
                    "name": name,
                    "feature_type": feature_type,
                    "latitude": latitude,
                    "longitude": longitude,
                    "properties": json.dumps(properties),
                },
            )

            imported += 1

        db.commit()

    return imported


if __name__ == "__main__":
    geojson_file = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "data/osm_features.geojson"
    )

    count = import_osm_geojson(geojson_file)

    print(
        f"Imported or updated {count} OSM features."
    )