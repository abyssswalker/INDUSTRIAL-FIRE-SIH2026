"""
merge_industrial_features.py

Takes Clusters.csv (fire clusters from cluster.py) and
industrial_areas_chhattisgarh.gpkg (fake or real industrial sites),
and adds, for every fire record:
    - nearest_industrial_distance_m : distance in meters to closest industrial feature
    - nearest_industrial_type       : what kind of industrial feature it is
    - industrial_count_5km          : how many industrial features are within 5 km

Output: DataBase/Cluster/Clusters_with_industrial.csv
"""

from pathlib import Path
import pandas as pd
import geopandas as gpd
from pyproj import Transformer
from scipy.spatial import cKDTree
import numpy as np

main_dir = Path(__file__).resolve().parent
data_dir = main_dir.parent / "DataBase"

clusters_path = data_dir / "Cluster" / "Clusters.csv"
industrial_path = data_dir / "industrial_areas_chhattisgarh.gpkg"
output_path = data_dir / "Cluster" / "Clusters_with_industrial.csv"

# --- load data ---
fires = pd.read_csv(clusters_path)
industrial = gpd.read_file(industrial_path)

# --- project both to meters (EPSG:32644, same as cluster.py) ---
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32644", always_xy=True)

fires["x_m"], fires["y_m"] = transformer.transform(
    fires["longitude"].values, fires["latitude"].values
)

# industrial geometries can be points or polygons — use centroid for a single x/y per feature
industrial = industrial.to_crs(epsg=4326)  # make sure it's in lat/lon first
industrial["centroid"] = industrial.geometry.centroid
ind_lon = industrial["centroid"].x.values
ind_lat = industrial["centroid"].y.values
ind_x, ind_y = transformer.transform(ind_lon, ind_lat)

# a readable "type" label per industrial feature, pulling from whichever tag column is present
def get_type(row):
    for col in ["landuse", "man_made", "power"]:
        if col in row and pd.notna(row[col]):
            return f"{col}={row[col]}"
    return "unknown"

industrial["feature_type"] = industrial.apply(get_type, axis=1)

# --- build KD-tree for fast nearest-neighbor + radius search ---
industrial_coords = np.column_stack([ind_x, ind_y])
tree = cKDTree(industrial_coords)

fire_coords = fires[["x_m", "y_m"]].values

# nearest distance + index
distances, nearest_idx = tree.query(fire_coords, k=1)
fires["nearest_industrial_distance_m"] = distances
fires["nearest_industrial_type"] = industrial["feature_type"].values[nearest_idx]

# count of industrial features within 5km (5000m)
counts_5km = tree.query_ball_point(fire_coords, r=5000, return_length=True)
fires["industrial_count_5km"] = counts_5km

# --- save ---
output_path.parent.mkdir(parents=True, exist_ok=True)
fires.to_csv(output_path, index=False)

print(f"Saved {len(fires)} rows with industrial features to {output_path}")
print(fires[[
    "cluster_id", "detection_count",
    "nearest_industrial_distance_m", "nearest_industrial_type",
    "industrial_count_5km"
]].head(10))
