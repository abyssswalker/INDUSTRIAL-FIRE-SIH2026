"""
step_e_classifier.py

Step E of the rule-based classifier build — the final step.
Combines all 4 signals into nested if/elif/else rules to assign each
cluster a first-pass label: industrial / wildfire / uncertain.

*** IMPORTANT: these thresholds are a FIRST DRAFT, not final. ***
Per the original plan, thresholds should be tuned by eyeballing 10-20
clusters on a map (e.g. plot cluster centroids + labels in QGIS or
just centroid_lat/centroid_lon on Google Maps) and adjusting until the
labels look right. Treat this run as a starting point to review, not
a finished answer.

Input:  DataBase/Cluster/cluster_features_step_c.csv (all 4 signals)
Output: DataBase/Cluster/cluster_labeled.csv (adds a 'label' column)
"""

from pathlib import Path
import pandas as pd

main_dir = Path(__file__).resolve().parent
data_dir = main_dir.parent / "DataBase"

input_path = data_dir / "Cluster" / "cluster_features_step_c.csv"
output_path = data_dir / "Cluster" / "cluster_labeled.csv"

df = pd.read_csv(input_path)

# --- THRESHOLDS (2nd draft — loosened after 1st run gave almost no "industrial" labels) ---
# Note: fake industrial data is sparse/randomly scattered, so distances to it are
# naturally larger than they'd be with real, denser OSM data. Loosen further or
# tighten back up once real data is swapped in.
RECURRENCE_HIGH = 15           # detections/month — "frequent" source
RECURRENCE_LOW = 3             # detections/month — "rare/one-off" source
FRP_CV_STEADY = 0.6            # below this = fairly steady heat output
INDUSTRIAL_DISTANCE_CLOSE = 10000   # meters — "near" an industrial feature
DAYNIGHT_SKEW_HIGH = 0.75       # ratio above this = heavily daytime-skewed (wildfire-like)


def classify(row):
    recurrence = row["recurrence_rate"]
    frp_cv = row["frp_cv"]
    distance = row["nearest_industrial_distance_m"]
    daynight_ratio = row["daynight_ratio"]

    # strong industrial signal: frequent, steady heat, close to a known industrial
    # feature, AND not heavily daytime-skewed (24/7 sources like flares/kilns show
    # more balanced day/night detections than wildfires do)
    if (
        recurrence > RECURRENCE_HIGH
        and distance < INDUSTRIAL_DISTANCE_CLOSE
        and frp_cv < FRP_CV_STEADY
        and daynight_ratio < DAYNIGHT_SKEW_HIGH
    ):
        return "industrial"

    # strong wildfire signal: rare/one-off, erratic heat, far from industrial,
    # and heavily skewed toward daytime detections (matches natural fire behavior)
    elif (
        recurrence <= RECURRENCE_LOW
        and distance > INDUSTRIAL_DISTANCE_CLOSE
        and daynight_ratio >= DAYNIGHT_SKEW_HIGH
    ):
        return "wildfire"

    # doesn't clearly fit either — flag for manual review
    else:
        return "uncertain"


df["label"] = df.apply(classify, axis=1)

df.to_csv(output_path, index=False)

print(f"Saved {len(df)} labeled clusters to {output_path}")
print()
print("Label distribution:")
print(df["label"].value_counts())
print()
print("Sample of each label:")
for lbl in df["label"].unique():
    print(f"\n--- {lbl} ---")
    print(df[df["label"] == lbl][[
        "cluster_id", "recurrence_rate", "frp_cv",
        "nearest_industrial_distance_m", "daynight_ratio", "label"
    ]].head(5))
