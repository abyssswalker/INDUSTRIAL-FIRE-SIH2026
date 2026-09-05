"""
step_c_daynight_ratio.py

Step C of the rule-based classifier build.
Adds, for each fire cluster:
    - day_count       : number of detections flagged as Day ('D')
    - night_count     : number of detections flagged as Night ('N')
    - daynight_ratio  : day_count / (day_count + night_count)
                         (close to 1 = mostly daytime detections,
                          close to 0 = mostly nighttime,
                          around 0.5 = detected consistently both day and night —
                          often a signature of a persistent industrial heat source)

Input:  DataBase/Cluster/Clusters_with_industrial.csv (raw detections)
        DataBase/Cluster/cluster_features_step_b.csv   (Step A+B output)
Output: DataBase/Cluster/cluster_features_step_c.csv    (Step A+B columns + daynight columns)

Run this, check the printed table looks sane, THEN we move to Step D.
"""

from pathlib import Path
import pandas as pd

main_dir = Path(__file__).resolve().parent
data_dir = main_dir.parent / "DataBase"

raw_path = data_dir / "Cluster" / "Clusters_with_real_industrial.csv"
step_b_path = data_dir / "Cluster" / "cluster_features_step_b.csv"
output_path = data_dir / "Cluster" / "cluster_features_step_c.csv"

raw = pd.read_csv(raw_path)
step_b = pd.read_csv(step_b_path)

# drop noise points, same as previous steps
raw = raw[raw["cluster_id"] != -1].copy()

# normalize the daynight column just in case of stray whitespace/casing
raw["daynight"] = raw["daynight"].astype(str).str.strip().str.upper()

daynight_stats = (
    raw.groupby("cluster_id")["daynight"]
    .value_counts()
    .unstack(fill_value=0)
    .reset_index()
)

# make sure both D and N columns exist even if one type never appears anywhere
for col in ["D", "N"]:
    if col not in daynight_stats.columns:
        daynight_stats[col] = 0

daynight_stats = daynight_stats.rename(columns={"D": "day_count", "N": "night_count"})
daynight_stats = daynight_stats[["cluster_id", "day_count", "night_count"]]

total = daynight_stats["day_count"] + daynight_stats["night_count"]
daynight_stats["daynight_ratio"] = (daynight_stats["day_count"] / total).fillna(0)

# merge onto Step A+B output using cluster_id as the shared key
merged = step_b.merge(daynight_stats, on="cluster_id", how="left")

merged.to_csv(output_path, index=False)

print(f"Saved {len(merged)} clusters to {output_path}")
print()
print(merged[[
    "cluster_id", "detection_count", "recurrence_rate", "frp_cv",
    "day_count", "night_count", "daynight_ratio"
]].sort_values("daynight_ratio", ascending=False).head(15))
