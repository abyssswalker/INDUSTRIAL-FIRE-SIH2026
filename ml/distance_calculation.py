import math
import pandas as pd
import numpy as np
from pathlib import Path
import json


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def load_osm_features(geojson_path):
    with open(geojson_path,encoding='utf-8') as f:
        data = json.load(f)

    features = []
    for element in data["features"]:
        geom = element["geometry"]
        if geom["type"] != "Point":
            continue  # skip non-point geometries for now

        lon, lat = (
            geom["coordinates"][0],
            geom["coordinates"][1],
        )  # GeoJSON order: [lon, lat]
        name = element["properties"].get("name", "Unnamed industrial feature")

        features.append({"name": name, "lat": lat, "lon": lon})

    return features


def find_nearest(cluster_lat, cluster_lon, osm_features):
    best_distance = float("inf")
    best_name = None
    best_lat = None
    best_lon = None

    for feature in osm_features:
        d = haversine(cluster_lat, cluster_lon, feature["lat"], feature["lon"])
        if d < best_distance:
            best_distance = d
            best_name = feature["name"]
            best_lat = feature["lat"]
            best_lon = feature["lon"]

    return best_name, best_distance, best_lat, best_lon


def count_within_radius(cluster_lat, cluster_lon, osm_features, radius_m):
    return sum(
        haversine(cluster_lat, cluster_lon, feature["lat"], feature["lon"]) <= radius_m
        for feature in osm_features
    )


def match_osm_distances():
    main_dir = Path(__file__).resolve().parent
    data_dir = main_dir.parent / "DataBase"
    osm_dir = data_dir / "osm"

    clusters = pd.read_csv(osm_dir / "cluster_csv_for_osm.csv")
    osm_features = load_osm_features(osm_dir / "osm_chatisgarh.geojson")

    print(
        f"Matching {len(clusters)} clusters against {len(osm_features)} OSM features..."
    )

    nearest_names = []
    nearest_distances = []
    nearest_lats = []
    nearest_lons = []
    osm_counts_within_5km = []


    for _, row in clusters.iterrows():
        name, distance, lat, lon = find_nearest(
            row["centroid_lat"], row["centroid_lon"], osm_features
        )
        nearest_names.append(name)
        nearest_distances.append(round(distance, 2))
        nearest_lats.append(lat)
        nearest_lons.append(lon)
        osm_counts_within_5km.append(
            count_within_radius(
                row["centroid_lat"], row["centroid_lon"], osm_features, 5000
            )
        )

    clusters["nearest_osm_feature"] = nearest_names
    clusters["distance_to_osm_m"] = nearest_distances
    clusters["nearest_osm_lat"] = nearest_lats
    clusters["nearest_osm_lon"] = nearest_lons
    clusters["osm_count_within_5km"] = osm_counts_within_5km
    
    
    clusters = clusters.drop_duplicates()

    output_path = osm_dir / "cluster_osm_distances.csv"
    clusters.to_csv(output_path, index=False)

    print(f"Saved to {output_path}")
    print(clusters.head(10))


if __name__ == "__main__":
    match_osm_distances()
