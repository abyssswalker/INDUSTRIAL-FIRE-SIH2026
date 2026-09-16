import asyncio
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.database import DATABASE_URL

BASE_DIR = Path(__file__).resolve().parent.parent

async def import_cluster_baselines_csv(csv_path: str) -> int:
    path = Path(csv_path)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()

    df = pd.read_csv(path, low_memory=False)

    required = {
        "cluster_id",
        "centroid_lat",
        "centroid_lon",
        "detection_count",
        "label",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    inserted = 0

    async with AsyncSession(engine) as session:
        for _, row in df.iterrows():
            cluster_id = int(row["cluster_id"])
            lat = float(row["centroid_lat"])
            lon = float(row["centroid_lon"])
            detection_count = int(row["detection_count"]) if pd.notna(row.get("detection_count")) else None
            label = str(row["label"]) if pd.notna(row.get("label")) else None

            frp_mean = float(row["frp_mean"]) if pd.notna(row.get("frp_mean")) else None
            frp_std = float(row["frp_std"]) if pd.notna(row.get("frp_std")) else None
            industrial_score = float(row["industrial_score"]) if pd.notna(row.get("industrial_score")) else None
            wildfire_score = float(row["wildfire_score"]) if pd.notna(row.get("wildfire_score")) else None
            recurrence_rate = float(row["recurrence_rate"]) if pd.notna(row.get("recurrence_rate")) else None
            nearest_ind_dist = float(row["nearest_industrial_distance_m"]) if pd.notna(row.get("nearest_industrial_distance_m")) else None
            nearest_ind_type = str(row["nearest_industrial_type"]) if pd.notna(row.get("nearest_industrial_type")) else None

            stmt = text("""
                INSERT INTO cluster_baselines (
                    cluster_id,
                    centroid_geom,
                    detection_count,
                    label,
                    frp_mean,
                    frp_std,
                    industrial_score,
                    wildfire_score,
                    recurrence_rate,
                    nearest_industrial_distance_m,
                    nearest_industrial_type
                ) VALUES (
                    :cluster_id,
                    ST_MakePoint(:lon, :lat),
                    :detection_count,
                    :label,
                    :frp_mean,
                    :frp_std,
                    :industrial_score,
                    :wildfire_score,
                    :recurrence_rate,
                    :nearest_ind_dist,
                    :nearest_ind_type
                )
                ON CONFLICT (cluster_id) DO UPDATE SET
                    centroid_geom = EXCLUDED.centroid_geom,
                    detection_count = EXCLUDED.detection_count,
                    label = EXCLUDED.label,
                    frp_mean = EXCLUDED.frp_mean,
                    frp_std = EXCLUDED.frp_std,
                    industrial_score = EXCLUDED.industrial_score,
                    wildfire_score = EXCLUDED.wildfire_score,
                    recurrence_rate = EXCLUDED.recurrence_rate,
                    nearest_industrial_distance_m = EXCLUDED.nearest_industrial_distance_m,
                    nearest_industrial_type = EXCLUDED.nearest_industrial_type
            """)

            await session.execute(
                stmt,
                {
                    "cluster_id": cluster_id,
                    "lon": lon,
                    "lat": lat,
                    "detection_count": detection_count,
                    "label": label,
                    "frp_mean": frp_mean,
                    "frp_std": frp_std,
                    "industrial_score": industrial_score,
                    "wildfire_score": wildfire_score,
                    "recurrence_rate": recurrence_rate,
                    "nearest_ind_dist": nearest_ind_dist,
                    "nearest_ind_type": nearest_ind_type,
                },
            )
            inserted += 1

        await session.commit()

    await engine.dispose()
    return inserted

if __name__ == "__main__":
    import sys
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "DataBase/Cluster/cluster_labeled_v2.csv"
    count = asyncio.run(import_cluster_baselines_csv(csv_file))
    print(f"Inserted/updated {count} cluster baseline rows.")