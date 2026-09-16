-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Fires (NASA FIRMS NRT points)
CREATE TABLE IF NOT EXISTS fires (
    id BIGSERIAL PRIMARY KEY,
    firms_id TEXT NOT NULL UNIQUE,
    frp NUMERIC(12,4),
    acq_timestamptz TIMESTAMPTZ,
    geom GEOMETRY(POINT, 4326) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fires_geom ON fires USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_fires_acq ON fires (acq_timestamptz);

-- Industrial areas (OSM + Bhuvan polygons)
CREATE TABLE IF NOT EXISTS industrial_areas (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,          -- 'osm' | 'bhuvan'
    name TEXT,
    feature_type TEXT,
    properties JSONB,
    geom GEOMETRY(POLYGON, 4326) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_industrial_geom ON industrial_areas USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_industrial_source ON industrial_areas (source);

-- Cluster baselines (for Z-score and ML labels)
CREATE TABLE IF NOT EXISTS cluster_baselines (
    cluster_id BIGINT PRIMARY KEY,
    centroid_geom GEOMETRY(POINT, 4326),
    frp_mean NUMERIC(12,4),
    frp_std NUMERIC(12,4),
    detection_count INT,
    label TEXT,
    industrial_score NUMERIC(12,6),
    wildfire_score NUMERIC(12,6),
    recurrence_rate NUMERIC(12,8),
    nearest_industrial_distance_m NUMERIC(18,6),
    nearest_industrial_type TEXT
);
CREATE INDEX IF NOT EXISTS idx_cluster_baselines_geom ON cluster_baselines USING GIST (centroid_geom);