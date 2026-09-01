"""
step_d_confirm_industrial.py

Step D of the rule-based classifier build.
This step doesn't compute anything new — nearest_industrial_distance_m and
nearest_industrial_type were already carried through since Step A. This just
confirms they're intact and sane before we combine everything in Step E.

Input:  DataBase/Cluster/cluster_features_step_c.csv (Step A+B+C output)

No output file — this is a check only.
"""

from pathlib import Path
import pandas as pd

main_dir = Path(__file__).resolve().parent
data_dir = main_dir.parent / "DataBase"

input_path = data_dir / "Cluster" / "cluster_features_step_c.csv"

df = pd.read_csv(input_path)

required_cols = [
    "cluster_id", "detection_count", "recurrence_rate",
    "frp_cv", "daynight_ratio",
    "nearest_industrial_distance_m", "nearest_industrial_type"
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    print(f"MISSING COLUMNS: {missing}")
else:
    print("All required columns present.")

print()
print("nearest_industrial_distance_m summary:")
print(df["nearest_industrial_distance_m"].describe())

print()
print("nearest_industrial_type value counts:")
print(df["nearest_industrial_type"].value_counts())

print()
print("Any missing (NaN) distances?", df["nearest_industrial_distance_m"].isna().sum())

print()
print("Sample rows, closest to industrial first:")
print(df[required_cols].sort_values("nearest_industrial_distance_m").head(10))
