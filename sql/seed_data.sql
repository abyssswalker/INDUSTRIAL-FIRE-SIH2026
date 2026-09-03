BEGIN;

--sample data
INSERT INTO osm_features (
    osm_id,
    name,
    feature_type,
    latitude,
    longitude,
    properties
)
VALUES
(
    'relation/11078270',
    'LG Polymers',
    'landuse=industrial',
    21.250000,
    81.630000,
    '{
        "name": "LG Polymers",
        "landuse": "industrial",
        "industrial": "chemical"
    }'
),
(
    'way/220001',
    'Bhilai Steel Plant',
    'industrial=steel',
    21.210000,
    81.430000,
    '{
        "name": "Bhilai Steel Plant",
        "industrial": "steel"
    }'
),
(
    'node/330001',
    'Example Thermal Power Station',
    'power=plant',
    21.500000,
    81.900000,
    '{
        "name": "Example Thermal Power Station",
        "power": "plant"
    }'
)
ON CONFLICT (osm_id) DO NOTHING;

INSERT INTO hotspots (
    cluster_id,
    centroid_lat,
    centroid_lon,
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
    classifier_version
)
VALUES
(
    101,
    21.251000,
    81.631000,
    18,
    '2026-06-01 12:00:00+00',
    '2026-09-01 13:00:00+00',
    3.0333,
    5.9341,
    42.5000,
    8.3000,
    0.1953,
    10,
    8,
    0.5556,
    'relation/11078270',
    420.5000,
    'landuse=industrial',
    'LG Polymers',
    'industrial',
    NULL,
    'rule-v1'
),
(
    102,
    21.320000,
    81.720000,
    5,
    '2026-08-20 08:00:00+00',
    '2026-09-01 09:00:00+00',
    0.4000,
    12.5000,
    18.3000,
    9.8000,
    0.5355,
    5,
    0,
    1.0000,
    NULL,
    NULL,
    NULL,
    NULL,
    'wildfire',
    NULL,
    'rule-v1'
),
(
    103,
    21.450000,
    81.800000,
    3,
    '2026-08-28 20:00:00+00',
    '2026-09-01 20:00:00+00',
    0.1333,
    22.5000,
    10.2000,
    7.9000,
    0.7745,
    1,
    2,
    0.3333,
    'node/330001',
    4100.0000,
    'power=plant',
    'Example Thermal Power Station',
    'uncertain',
    NULL,
    'rule-v1'
);

INSERT INTO firms_detections (
    firms_id,
    latitude,
    longitude,
    detected_at,
    acq_date,
    acq_time,
    satellite,
    instrument,
    source,
    frp,
    confidence,
    day_night,
    brightness_ti4,
    brightness_ti5,
    cluster_id
)
VALUES
(
    'FIRMS-101-001',
    21.251000,
    81.631000,
    '2026-06-01 12:00:00+00',
    '2026-06-01',
    '12:00:00',
    'NOAA-20',
    'VIIRS',
    'VIIRS_NOAA20_NRT',
    35.4000,
    'h',
    'D',
    345.1000,
    295.0000,
    101
),
(
    'FIRMS-101-002',
    21.251500,
    81.630500,
    '2026-07-10 20:00:00+00',
    '2026-07-10',
    '20:00:00',
    'Suomi NPP',
    'VIIRS',
    'VIIRS_SNPP_NRT',
    49.6000,
    'h',
    'N',
    350.2000,
    297.1000,
    101
),
(
    'FIRMS-102-001',
    21.320000,
    81.720000,
    '2026-08-20 08:00:00+00',
    '2026-08-20',
    '08:00:00',
    'NOAA-20',
    'VIIRS',
    'VIIRS_NOAA20_NRT',
    18.3000,
    'n',
    'D',
    331.0000,
    293.4000,
    102
),
(
    'FIRMS-103-001',
    21.450000,
    81.800000,
    '2026-08-28 20:00:00+00',
    '2026-08-28',
    '20:00:00',
    'NOAA-20',
    'VIIRS',
    'VIIRS_NOAA20_NRT',
    10.2000,
    'n',
    'N',
    328.5000,
    292.9000,
    103
);

COMMIT;