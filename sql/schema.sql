BEGIN;


-- OSM FEATURES

CREATE TABLE IF NOT EXISTS osm_features (
    id BIGSERIAL PRIMARY KEY,

    -- Example: relation/11078270
    osm_id TEXT NOT NULL UNIQUE,

    -- Human-readable feature name
    name TEXT,

    -- Raw or normalized OSM tag
    feature_type TEXT NOT NULL,

    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,

    -- Full OSM properties can be retained here
    properties JSONB,

    source TEXT NOT NULL DEFAULT 'OpenStreetMap',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT osm_latitude_check
        CHECK (latitude BETWEEN -90 AND 90),

    CONSTRAINT osm_longitude_check
        CHECK (longitude BETWEEN -180 AND 180)
);

-- HOTSPOTS
CREATE TABLE IF NOT EXISTS hotspots (
    cluster_id BIGINT PRIMARY KEY,

    centroid_lat NUMERIC(9, 6) NOT NULL,
    centroid_lon NUMERIC(9, 6) NOT NULL,

    detection_count INTEGER NOT NULL DEFAULT 0,

    first_seen TIMESTAMPTZ NOT NULL,
    last_seen TIMESTAMPTZ NOT NULL,

    months_active NUMERIC(12, 4),
    recurrence_rate NUMERIC(12, 4),

    frp_mean NUMERIC(12, 4),
    frp_std NUMERIC(12, 4),
    frp_cv NUMERIC(12, 6),

    day_count INTEGER NOT NULL DEFAULT 0,
    night_count INTEGER NOT NULL DEFAULT 0,
    daynight_ratio NUMERIC(12, 6),

    -- Joined from osm_features.osm_id
    nearest_osm_id TEXT,

    nearest_industrial_distance_m NUMERIC(14, 4),


    nearest_industrial_type TEXT,

    nearest_industrial_name TEXT,

    -- application labels
    classification TEXT NOT NULL DEFAULT 'uncertain',

    -- NULL until XGBoost or another numeric model is available
    confidence NUMERIC(6, 5),

    classifier_version TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT hotspots_latitude_check
        CHECK (centroid_lat BETWEEN -90 AND 90),

    CONSTRAINT hotspots_longitude_check
        CHECK (centroid_lon BETWEEN -180 AND 180),

    CONSTRAINT hotspots_detection_count_check
        CHECK (detection_count >= 0),

    CONSTRAINT hotspots_day_count_check
        CHECK (day_count >= 0),

    CONSTRAINT hotspots_night_count_check
        CHECK (night_count >= 0),

    CONSTRAINT hotspots_frp_mean_check
        CHECK (frp_mean IS NULL OR frp_mean >= 0),

    CONSTRAINT hotspots_frp_std_check
        CHECK (frp_std IS NULL OR frp_std >= 0),

    CONSTRAINT hotspots_frp_cv_check
        CHECK (frp_cv IS NULL OR frp_cv >= 0),

    CONSTRAINT hotspots_distance_check
        CHECK (
            nearest_industrial_distance_m IS NULL
            OR nearest_industrial_distance_m >= 0
        ),

    CONSTRAINT hotspots_classification_check
        CHECK (
            classification IN (
                'industrial',
                'wildfire',
                'uncertain'
            )
        ),

    CONSTRAINT hotspots_confidence_check
        CHECK (
            confidence IS NULL
            OR confidence BETWEEN 0 AND 1
        ),

    CONSTRAINT hotspots_date_check
        CHECK (last_seen >= first_seen),

    CONSTRAINT hotspots_osm_fk
        FOREIGN KEY (nearest_osm_id)
        REFERENCES osm_features(osm_id)
        ON DELETE SET NULL
);
-

CREATE TABLE IF NOT EXISTS firms_detections (
    id BIGSERIAL PRIMARY KEY,

    firms_id TEXT,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,

    detected_at TIMESTAMPTZ NOT NULL,

    acq_date DATE,
    acq_time TIME,

    satellite TEXT,
    instrument TEXT,
    source TEXT,

    frp NUMERIC(12, 4),
    confidence TEXT,
    day_night CHAR(1),

    brightness_ti4 NUMERIC(12, 4),
    brightness_ti5 NUMERIC(12, 4),

    cluster_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT firms_latitude_check
        CHECK (latitude BETWEEN -90 AND 90),

    CONSTRAINT firms_longitude_check
        CHECK (longitude BETWEEN -180 AND 180),

    CONSTRAINT firms_daynight_check
        CHECK (
            day_night IS NULL
            OR day_night IN ('D', 'N')
        ),

    CONSTRAINT firms_frp_check
        CHECK (frp IS NULL OR frp >= 0),

    CONSTRAINT firms_cluster_fk
        FOREIGN KEY (cluster_id)
        REFERENCES hotspots(cluster_id)
        ON DELETE SET NULL
);

-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS osm_features_type_idx
ON osm_features(feature_type);

CREATE INDEX IF NOT EXISTS osm_features_name_idx
ON osm_features(name);

CREATE INDEX IF NOT EXISTS osm_features_coordinates_idx
ON osm_features(latitude, longitude);

CREATE INDEX IF NOT EXISTS osm_features_properties_idx
ON osm_features USING GIN(properties);

CREATE INDEX IF NOT EXISTS hotspots_classification_idx
ON hotspots(classification);

CREATE INDEX IF NOT EXISTS hotspots_first_seen_idx
ON hotspots(first_seen);

CREATE INDEX IF NOT EXISTS hotspots_last_seen_idx
ON hotspots(last_seen);

CREATE INDEX IF NOT EXISTS hotspots_osm_id_idx
ON hotspots(nearest_osm_id);

CREATE INDEX IF NOT EXISTS hotspots_coordinates_idx
ON hotspots(centroid_lat, centroid_lon);

CREATE INDEX IF NOT EXISTS firms_detected_at_idx
ON firms_detections(detected_at);

CREATE INDEX IF NOT EXISTS firms_cluster_id_idx
ON firms_detections(cluster_id);

CREATE INDEX IF NOT EXISTS firms_coordinates_idx
ON firms_detections(latitude, longitude);

COMMIT;