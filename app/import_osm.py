from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.database import SessionLocal
from app.models import OSMFeature

BASE_DIR = Path(__file__).resolve().parent.parent


def import_osm_csv(csv_path: str) -> int:
    path = Path(csv_path)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"OSM file was not found: {path}")

    df = pd.read_csv(path, low_memory=False)

    required_columns = {"osm_id", "name", "feature_type", "latitude", "longitude"}
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns in OSM CSV: {sorted(missing)}")

    rows = []
    for _, row in df.iterrows():
        rows.append({
            "osm_id": str(row["osm_id"]),
            "name": None if pd.isna(row["name"]) else str(row["name"]),
            "feature_type": str(row["feature_type"]),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "properties": None,
            "source": "OpenStreetMap",
        })

    with SessionLocal() as db:
        stmt = sqlite_insert(OSMFeature).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["osm_id"],
            set_={
                "name": stmt.excluded.name,
                "feature_type": stmt.excluded.feature_type,
                "latitude": stmt.excluded.latitude,
                "longitude": stmt.excluded.longitude,
                "source": stmt.excluded.source,
                "updated_at": stmt.excluded.updated_at,
            },
        )
        db.execute(stmt)
        db.commit()

    return len(rows)


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "DataBase/osm/osm_chatisgarh.geojson"
    print(f"Imported or updated {import_osm_csv(csv_file)} OSM rows.")