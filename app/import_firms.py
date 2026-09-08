from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.database import SessionLocal
from app.models import ClusterSummary

BASE_DIR = Path(__file__).resolve().parent.parent

EXPECTED_COLUMNS = [
    "cluster_id",
    "detection_count",
    "first_seen",
    "last_seen",
    "centroid_lat",
    "centroid_lon",
    "nearest_industrial_distance_m",
    "nearest_industrial_type",
    "months_active",
    "recurrence_rate",
    "frp_mean",
    "frp_std",
    "frp_cv",
    "day_count",
    "night_count",
    "daynight_ratio",
    "industrial_score",
    "wildfire_score",
    "label",
]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def parse_dt(value):
    if pd.isna(value):
        return None
    return pd.to_datetime(value)


def import_clusters_csv(csv_path: str) -> int:
    path = Path(csv_path)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"CSV file was not found: {path}")

    df = pd.read_csv(path, low_memory=False)
    df = normalize_columns(df)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    rows = []
    for _, row in df.iterrows():
        rows.append({
            "cluster_id": int(row["cluster_id"]),
            "detection_count": None if pd.isna(row["detection_count"]) else int(row["detection_count"]),
            "first_seen": parse_dt(row["first_seen"]),
            "last_seen": parse_dt(row["last_seen"]),
            "centroid_lat": None if pd.isna(row["centroid_lat"]) else float(row["centroid_lat"]),
            "centroid_lon": None if pd.isna(row["centroid_lon"]) else float(row["centroid_lon"]),
            "nearest_industrial_distance_m": None if pd.isna(row["nearest_industrial_distance_m"]) else float(row["nearest_industrial_distance_m"]),
            "nearest_industrial_type": None if pd.isna(row["nearest_industrial_type"]) else str(row["nearest_industrial_type"]),
            "months_active": None if pd.isna(row["months_active"]) else float(row["months_active"]),
            "recurrence_rate": None if pd.isna(row["recurrence_rate"]) else float(row["recurrence_rate"]),
            "frp_mean": None if pd.isna(row["frp_mean"]) else float(row["frp_mean"]),
            "frp_std": None if pd.isna(row["frp_std"]) else float(row["frp_std"]),
            "frp_cv": None if pd.isna(row["frp_cv"]) else float(row["frp_cv"]),
            "day_count": None if pd.isna(row["day_count"]) else int(row["day_count"]),
            "night_count": None if pd.isna(row["night_count"]) else int(row["night_count"]),
            "daynight_ratio": None if pd.isna(row["daynight_ratio"]) else float(row["daynight_ratio"]),
            "industrial_score": None if pd.isna(row["industrial_score"]) else float(row["industrial_score"]),
            "wildfire_score": None if pd.isna(row["wildfire_score"]) else float(row["wildfire_score"]),
            "label": None if pd.isna(row["label"]) else str(row["label"]),
        })

    with SessionLocal() as db:
        stmt = sqlite_insert(ClusterSummary).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["cluster_id"],
            set_={
                "detection_count": stmt.excluded.detection_count,
                "first_seen": stmt.excluded.first_seen,
                "last_seen": stmt.excluded.last_seen,
                "centroid_lat": stmt.excluded.centroid_lat,
                "centroid_lon": stmt.excluded.centroid_lon,
                "nearest_industrial_distance_m": stmt.excluded.nearest_industrial_distance_m,
                "nearest_industrial_type": stmt.excluded.nearest_industrial_type,
                "months_active": stmt.excluded.months_active,
                "recurrence_rate": stmt.excluded.recurrence_rate,
                "frp_mean": stmt.excluded.frp_mean,
                "frp_std": stmt.excluded.frp_std,
                "frp_cv": stmt.excluded.frp_cv,
                "day_count": stmt.excluded.day_count,
                "night_count": stmt.excluded.night_count,
                "daynight_ratio": stmt.excluded.daynight_ratio,
                "industrial_score": stmt.excluded.industrial_score,
                "wildfire_score": stmt.excluded.wildfire_score,
                "label": stmt.excluded.label,
            },
        )
        db.execute(stmt)
        db.commit()

    return len(rows)


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "DataBase/Cluster/cluster_labeled_v2.csv"
    print(f"Imported or updated {import_clusters_csv(csv_file)} rows.")