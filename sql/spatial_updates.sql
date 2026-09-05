BEGIN;

CREATE EXTENSION IF NOT EXISTS postgis;

ALTER TABLE osm_features
ADD COLUMN IF NOT EXISTS geom GEOGRAPHY(Point, 4326);

ALTER TABLE hotspots
ADD COLUMN IF NOT EXISTS geom GEOGRAPHY(Point, 4326);

ALTER TABLE firms_detections
ADD COLUMN IF NOT EXISTS geom GEOGRAPHY(Point, 4326);

UPDATE osm_features
SET geom = ST_SetSRID(
    ST_MakePoint(
        longitude::DOUBLE PRECISION,
        latitude::DOUBLE PRECISION
    ),
    4326
)::GEOGRAPHY
WHERE geom IS NULL;

UPDATE hotspots
SET geom = ST_SetSRID(
    ST_MakePoint(
        centroid_lon::DOUBLE PRECISION,
        centroid_lat::DOUBLE PRECISION
    ),
    4326
)::GEOGRAPHY
WHERE geom IS NULL;

UPDATE firms_detections
SET geom = ST_SetSRID(
    ST_MakePoint(
        longitude::DOUBLE PRECISION,
        latitude::DOUBLE PRECISION
    ),
    4326
)::GEOGRAPHY
WHERE geom IS NULL;

CREATE INDEX IF NOT EXISTS osm_features_geom_idx
ON osm_features
USING GIST (geom);

CREATE INDEX IF NOT EXISTS hotspots_geom_idx
ON hotspots
USING GIST (geom);

CREATE INDEX IF NOT EXISTS firms_geom_idx
ON firms_detections
USING GIST (geom);

COMMIT;