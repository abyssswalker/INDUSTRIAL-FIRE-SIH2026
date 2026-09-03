-- ============================================================
-- All hotspot clusters
-- ============================================================

SELECT
    cluster_id,
    centroid_lat,
    centroid_lon,
    detection_count,
    first_seen,
    last_seen,
    classification,
    confidence,
    nearest_industrial_name,
    nearest_industrial_type,
    nearest_industrial_distance_m
FROM hotspots
ORDER BY last_seen DESC;


-- ============================================================
-- Three-state classification counts
-- ============================================================

SELECT
    classification,
    COUNT(*) AS total
FROM hotspots
GROUP BY classification
ORDER BY classification;


-- ============================================================
-- Industrial hotspots
-- ============================================================

SELECT *
FROM hotspots
WHERE classification = 'industrial'
ORDER BY confidence DESC NULLS LAST, last_seen DESC;


-- ============================================================
-- Wildfire hotspots
-- ============================================================

SELECT *
FROM hotspots
WHERE classification = 'wildfire'
ORDER BY confidence DESC NULLS LAST, last_seen DESC;


-- ============================================================
-- Uncertain hotspots
-- ============================================================

SELECT *
FROM hotspots
WHERE classification = 'uncertain'
ORDER BY last_seen DESC;


-- ============================================================
-- Join feature name and raw OSM type from osm_features
-- ============================================================

SELECT
    h.cluster_id,
    h.classification,
    h.confidence,
    h.nearest_osm_id,
    o.name AS nearest_industrial_name,
    o.feature_type AS nearest_industrial_type,
    h.nearest_industrial_distance_m
FROM hotspots h
LEFT JOIN osm_features o
    ON h.nearest_osm_id = o.osm_id;


-- ============================================================
-- Date-range query
-- ============================================================

SELECT *
FROM hotspots
WHERE first_seen >= '2026-08-01 00:00:00+00'
  AND last_seen < '2026-09-04 00:00:00+00'
ORDER BY last_seen DESC;


-- ============================================================
-- High recurrence clusters
-- ============================================================

SELECT *
FROM hotspots
WHERE recurrence_rate >= 5
ORDER BY recurrence_rate DESC;


-- ============================================================
-- Raw FIRMS observations for one cluster
-- ============================================================

SELECT *
FROM firms_detections
WHERE cluster_id = 101
ORDER BY detected_at;


-- ============================================================
-- Check missing OSM joins
-- ============================================================

SELECT *
FROM hotspots
WHERE nearest_osm_id IS NOT NULL
  AND nearest_industrial_name IS NULL;


-- ============================================================
-- Check impossible confidence values
-- ============================================================

SELECT *
FROM hotspots
WHERE confidence IS NOT NULL
  AND (confidence < 0 OR confidence > 1);