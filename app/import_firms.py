import asyncio
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.database import DATABASE_URL

BASE_DIR = Path(__file__).resolve().parent.parent

async def import_firms_csv(csv_path: str) -> int:
    path = Path(csv_path)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()

    df = pd.read_csv(path, low_memory=False)

    required = {"latitude", "longitude", "frp", "acq_DateTime"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    engine = create_async_engine(DATABASE_URL, echo=False, future=True)

    inserted = 0
    async with AsyncSession(engine) as session:
        for _, row in df.iterrows():
            firms_id = f"{row['latitude']}_{row['longitude']}_{row.get('acq_DateTime', '')}_{row.get('cluster_id', '')}"
            frp = float(row["frp"]) if pd.notna(row.get("frp")) else None
            acq_time = pd.to_datetime(row["acq_DateTime"]) if pd.notna(row.get("acq_DateTime")) else None
            lon = float(row["longitude"])
            lat = float(row["latitude"])

            stmt = text("""
                INSERT INTO fires (firms_id, frp, acq_timestamptz, geom)
                VALUES (:firms_id, :frp, :acq_time, ST_MakePoint(:lon, :lat))
                ON CONFLICT (firms_id) DO UPDATE SET
                    frp = EXCLUDED.frp,
                    acq_timestamptz = EXCLUDED.acq_timestamptz,
                    geom = EXCLUDED.geom
            """)

            await session.execute(
                stmt,
                {
                    "firms_id": str(firms_id),
                    "frp": frp,
                    "acq_time": acq_time,
                    "lon": lon,
                    "lat": lat,
                },
            )
            inserted += 1

        await session.commit()

    await engine.dispose()
    return inserted

if __name__ == "__main__":
    import sys
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "DataBase/chatisgarh_clean.csv"
    count = asyncio.run(import_firms_csv(csv_file))
    print(f"Inserted/updated {count} fire rows.")