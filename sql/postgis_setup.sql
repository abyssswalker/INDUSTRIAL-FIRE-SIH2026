CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Optional: ensure a spatial index exists if you import industrial polygons directly.
-- CREATE TABLE IF NOT EXISTS industrial_zones (
--   id SERIAL PRIMARY KEY,
--   name TEXT,
--   zone_type TEXT,
--   geom GEOMETRY(MultiPolygon, 4326)
-- );
--
-- CREATE TABLE IF NOT EXISTS fire_points (
--   id SERIAL PRIMARY KEY,
--   source TEXT,
--   frp DOUBLE PRECISION,
--   latitude DOUBLE PRECISION,
--   longitude DOUBLE PRECISION,
--   detected_at TIMESTAMPTZ,
--   geom GEOMETRY(Point, 4326)
-- );

-- Reusable index for spatial tables.
-- CREATE INDEX IF NOT EXISTS idx_industrial_zones_geom
-- ON industrial_zones USING GIST (geom);
--
-- CREATE INDEX IF NOT EXISTS idx_fire_points_geom
-- ON fire_points USING GIST (geom);

SELECT PostGIS_Version();
