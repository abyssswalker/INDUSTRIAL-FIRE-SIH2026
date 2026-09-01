"""
step_b_frp_variance.py

Step B of the rule-based classifier build.
Adds, for each fire cluster:
    - frp_mean : average Fire Radiative Power for the cluster
    - frp_std  : standard deviation of FRP for the cluster
    - frp_cv   : coefficient of variation = frp_std / frp_mean
                 (low cv = steady/consistent heat output, like an industrial source
                  high cv = spiky/erratic heat output, more like a spreading wildfire)

Input:  DataBase/Cluster/Clusters_with_industrial.csv (raw detections)
        DataBase/Cluster/cluster_features_step_a.csv   (Step A output)
Output: DataBase/Cluster/cluster_features_step_b.csv    (Step A columns + frp columns)

Run this, check the printed table looks sane, THEN we move to Step C.
"""

from pathlib import Path
import pandas as pd

main_dir = Path(__file__).resolve().parent
data_dir = main_dir.parent / "DataBase"

raw_path = data_dir / "Cluster" / "Clusters_with_industrial.csv"
step_a_path = data_dir / "Cluster" / "cluster_features_step_a.csv"
output_path = data_dir / "Cluster" / "cluster_features_step_b.csv"

raw = pd.read_csv(raw_path)
step_a = pd.read_csv(step_a_path)

# drop noise points, same as Step A
raw = raw[raw["cluster_id"] != -1].copy()

# per-cluster FRP stats
frp_stats = raw.groupby("cluster_id")["frp"].agg(
    frp_mean="mean",
    frp_std="std",
).reset_index()

# std can be NaN for clusters with only 1 detection — fill with 0 (no variation to measure)
frp_stats["frp_std"] = frp_stats["frp_std"].fillna(0)

# coefficient of variation; guard against divide-by-zero if frp_mean is 0
frp_stats["frp_cv"] = frp_stats["frp_std"] / frp_stats["frp_mean"].replace(0, pd.NA)
frp_stats["frp_cv"] = frp_stats["frp_cv"].fillna(0)

# merge onto Step A's output using cluster_id as the shared key
merged = step_a.merge(frp_stats, on="cluster_id", how="left")

merged.to_csv(output_path, index=False)

print(f"Saved {len(merged)} clusters to {output_path}")
print()
print(merged[[
    "cluster_id", "detection_count", "recurrence_rate", "frp_mean", "frp_std", "frp_cv"
]].sort_values("frp_cv", ascending=False).head(15))
