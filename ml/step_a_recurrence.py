"""
step_a_recurrence.py

Step A of the rule-based classifier build.
Computes, for each fire cluster:
    - months_active   : how many months apart the first and last detection are
    - recurrence_rate  : detection_count / months_active
                         (a high value = frequent/persistent thermal source)

Input:  DataBase/Cluster/Clusters_with_industrial.csv
Output: DataBase/Cluster/cluster_features_step_a.csv  (one row per cluster_id)

Run this, check the printed table looks sane, THEN we move to Step B.
"""

from pathlib import Path
import pandas as pd

main_dir = Path(__file__).resolve().parent
data_dir = main_dir.parent / "DataBase"

input_path = data_dir / "Cluster" / "Clusters_with_industrial.csv"
output_path = data_dir / "Cluster" / "cluster_features_step_a.csv"

df = pd.read_csv(input_path)

# drop noise points (cluster_id == -1 from DBSCAN) — they aren't real clusters
df = df[df["cluster_id"] != -1].copy()

# parse the acquisition datetime column
df["acq_DateTime"] = pd.to_datetime(df["acq_DateTime"])

# per-cluster aggregation
agg = df.groupby("cluster_id").agg(
    detection_count=("cluster_id", "size"),
    first_seen=("acq_DateTime", "min"),
    last_seen=("acq_DateTime", "max"),
    centroid_lat=("centroid_lat", "first"),
    centroid_lon=("centroid_lon", "first"),
    nearest_industrial_distance_m=("nearest_industrial_distance_m", "first"),
    nearest_industrial_type=("nearest_industrial_type", "first"),
).reset_index()

# months_active: span between first and last detection, in months
# minimum of 1 to avoid divide-by-zero for clusters seen on a single day
agg["months_active"] = (
    (agg["last_seen"] - agg["first_seen"]).dt.days / 30
).clip(lower=1)

agg["recurrence_rate"] = agg["detection_count"] / agg["months_active"]

agg.to_csv(output_path, index=False)

print(f"Saved {len(agg)} clusters to {output_path}")
print()
print(agg[[
    "cluster_id", "detection_count", "months_active", "recurrence_rate"
]].sort_values("recurrence_rate", ascending=False).head(15))
