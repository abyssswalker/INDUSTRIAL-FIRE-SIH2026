"""
Generate fake/synthetic industrial areas data for Chhattisgarh.
Drop-in replacement for the real OSM pull in osm.py — matches the same
schema (geometry + tags) so cluster.py and downstream code need zero changes.

Run this locally in your .venv:
    python generate_fake_industrial_data.py
"""

import random
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point

random.seed(42)  # reproducible fake data

# --- Chhattisgarh's approximate bounding box ---
MIN_LON, MAX_LON = 80.15, 84.4
MIN_LAT, MAX_LAT = 17.75, 24.1

SAVE_PATH = "../DataBase/industrial_areas_chhattisgarh.gpkg"  # same path your real pipeline uses

# Rough locations of some real industrial hubs in Chhattisgarh, to make
# fake clusters look plausible instead of pure random noise.
HUB_CENTERS = {
    "Bhilai (steel)": (81.3509, 21.2094),
    "Raipur (industrial belt)": (81.6296, 21.2514),
    "Korba (power/coal)": (82.6805, 22.3595),
    "Raigarh (steel/power)": (83.3950, 21.8974),
    "Durg": (81.2849, 21.1904),
    "Bilaspur": (82.1409, 22.0797),
    "Jagdalpur": (82.0338, 19.0748),
}


def random_point_near(center_lon, center_lat, spread=0.15):
    lon = center_lon + random.uniform(-spread, spread)
    lat = center_lat + random.uniform(-spread, spread)
    return lon, lat


def make_polygon(center_lon, center_lat, size=0.01):
    """Make a small irregular-ish rectangular polygon around a center point."""
    dx = size * random.uniform(0.7, 1.3)
    dy = size * random.uniform(0.7, 1.3)
    return Polygon([
        (center_lon - dx, center_lat - dy),
        (center_lon + dx, center_lat - dy),
        (center_lon + dx, center_lat + dy),
        (center_lon - dx, center_lat + dy),
    ])


def generate_landuse_industrial(n=40):
    rows = []
    for i in range(n):
        hub = random.choice(list(HUB_CENTERS.keys()))
        clon, clat = HUB_CENTERS[hub]
        lon, lat = random_point_near(clon, clat, spread=0.2)
        geom = make_polygon(lon, lat, size=random.uniform(0.005, 0.02))
        rows.append({
            "geometry": geom,
            "landuse": "industrial",
            "name": f"Fake Industrial Zone {i+1} ({hub})",
        })
    return rows


def generate_points(n, tag_key, tag_values, name_prefix):
    rows = []
    for i in range(n):
        hub = random.choice(list(HUB_CENTERS.keys()))
        clon, clat = HUB_CENTERS[hub]
        lon, lat = random_point_near(clon, clat, spread=0.25)
        rows.append({
            "geometry": Point(lon, lat),
            tag_key: random.choice(tag_values),
            "name": f"{name_prefix} {i+1} ({hub})",
        })
    return rows


def main():
    all_rows = []
    all_rows += generate_landuse_industrial(n=40)
    all_rows += generate_points(15, "man_made", ["works", "kiln"], "Fake Works/Kiln")
    all_rows += generate_points(10, "power", ["plant", "generator"], "Fake Power Site")

    gdf = gpd.GeoDataFrame(pd.DataFrame(all_rows), crs="EPSG:4326")

    gdf.to_file(SAVE_PATH, driver="GPKG")
    print(f"Saved {len(gdf)} fake industrial features to {SAVE_PATH}")
    print(gdf.head())


if __name__ == "__main__":
    main()
