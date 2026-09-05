"""
step_e_classifier_v2.py

Version 2 of the rule-based classifier — replaces the strict AND-based
logic with a points-based scoring system, and now actually uses
industrial_count_5km (which was computed but unused in v1).

Instead of requiring ALL conditions to pass at once, each piece of
evidence contributes points toward an overall "industrial-ness" score.
This lets strong evidence on one signal (e.g. being 65m from a real
factory) count meaningfully even if another signal is only moderate
(e.g. recurrence rate not sky-high) — cases that v1 was throwing into
'uncertain' despite strong evidence.

The resulting 'industrial_score' column is kept in the output too —
useful later as a rough confidence indicator, not just a flat label.

*** These point values and cutoffs are a reasoned starting point, ***
*** not the final answer — discuss with your teammate and adjust  ***
*** if the label distribution or map still looks off.             ***

Input:  DataBase/Cluster/cluster_features_step_c.csv (all 4+ signals)
Output: DataBase/Cluster/cluster_labeled_v2.csv (adds industrial_score + label)
"""

from pathlib import Path
import pandas as pd

main_dir = Path(__file__).resolve().parent
data_dir = main_dir.parent / "DataBase"

input_path = data_dir / "Cluster" / "cluster_features_step_c.csv"
output_path = data_dir / "Cluster" / "cluster_labeled_v2.csv"

df = pd.read_csv(input_path)


def score_industrial(row):
    score = 0
    distance = row["nearest_industrial_distance_m"]
    recurrence = row["recurrence_rate"]
    frp_cv = row["frp_cv"]
    count_5km = row.get("industrial_count_5km", 0)

    # --- distance to nearest industrial site ---
    if distance < 200:
        score += 3
    elif distance < 1000:
        score += 2
    elif distance < 5000:
        score += 1

    # --- recurrence (persistence) ---
    if recurrence > 20:
        score += 2
    elif recurrence > 10:
        score += 1

    # --- FRP steadiness ---
    if frp_cv < 0.6:
        score += 1

    # --- density of nearby industrial activity ---
    if count_5km > 5:
        score += 2
    elif count_5km > 1:
        score += 1

    return score


def score_wildfire(row):
    """A separate, simple wildfire score — high when evidence points
    AWAY from industrial (far away, rare, erratic, daytime-only)."""
    score = 0
    distance = row["nearest_industrial_distance_m"]
    recurrence = row["recurrence_rate"]
    daynight_ratio = row["daynight_ratio"]

    if distance > 10000:
        score += 2
    elif distance > 5000:
        score += 1

    if recurrence <= 3:
        score += 2
    elif recurrence <= 6:
        score += 1

    if daynight_ratio >= 0.9 or daynight_ratio <= 0.1:
        score += 1  # heavily one-sided day/night pattern

    return score


df["industrial_score"] = df.apply(score_industrial, axis=1)
df["wildfire_score"] = df.apply(score_wildfire, axis=1)


def classify(row):
    if row["industrial_score"] >= 5:
        return "industrial"
    elif row["wildfire_score"] >= 4:
        return "wildfire"
    else:
        return "uncertain"


df["label"] = df.apply(classify, axis=1)

df.to_csv(output_path, index=False)

print(f"Saved {len(df)} labeled clusters to {output_path}")
print()
print("Label distribution:")
print(df["label"].value_counts())
print()
print("Sample of each label (sorted by relevant score, strongest first):")
for lbl in df["label"].unique():
    sort_col = "industrial_score" if lbl == "industrial" else (
        "wildfire_score" if lbl == "wildfire" else "industrial_score"
    )
    print(f"\n--- {lbl} ---")
    print(df[df["label"] == lbl][[
        "cluster_id", "recurrence_rate", "frp_cv",
        "nearest_industrial_distance_m", "industrial_count_5km",
        "daynight_ratio", "industrial_score", "wildfire_score", "label"
    ]].sort_values(sort_col, ascending=False).head(5))
