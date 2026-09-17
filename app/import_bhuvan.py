import asyncio
import json
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.database import DATABASE_URL

BASE_DIR = Path(__file__).resolve().parent.parent

# Bhuvan data is intentionally disabled until a valid source dataset is available.
# This importer is kept as a placeholder for future use.

async def import_bhuvan_geojson(geojson_path: str) -> int:
    path = Path(geojson_path)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()

    with open(path, "r", encoding="utf-8") as f:
        gj = json.load(f)

    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    inserted = 0

    async with AsyncSession(engine) as session:
        for feature in gj.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry")
            if not geom or geom.get("type") != "Polygon":
                continue

            name = props.get("name") or props.get("industrial_name")
            feature_type = props.get("feature_type") or props.get("type") or "industrial"
            osm_id = props.get("osm_id") or props.get("id") or ""

            geom_json = json.dumps(geom)

            stmt = text("""
                INSERT INTO industrial_areas (source, name, feature_type, properties, geom)
                VALUES (
                    'bhuvan',
                    :name,
                    :feature_type,
                    :properties::jsonb,
                    ST_SetSRID(ST_GeomFromGeoJSON(:geom_json), 4326)
                )
                ON CONFLICT DO NOTHING
            """)

            await session.execute(
                stmt,
                {
                    "name": name,
                    "feature_type": feature_type,
                    "properties": json.dumps(props),
                    "geom_json": geom_json,
                },
            )
            inserted += 1

        await session.commit()

    await engine.dispose()
    return inserted

if __name__ == "__main__":
    print("Bhuvan import is disabled: no source dataset is available in DataBase/bhuvan yet.")