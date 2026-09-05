from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.database import SessionLocal


def clean_value(value):
    if pd.isna(value):
        return None

    return value

#this helps in importing data from nas need to change it after all data has been included
def parse_detected_at(row: pd.Series) -> datetime:
    date_value = str(row.get("acq_date"))
    time_value = str(row.get("acq_time"))

    time_value = time_value.zfill(4)

    date_time = datetime.strptime(
        f"{date_value} {time_value}",
        "%Y-%m-%d %H%M",
    )

    return date_time.replace(tzinfo=timezone.utc)


def import_firms_csv(csv_path: str) -> int:
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(
            f"FIRMS CSV was not found: {path}"
        )

    dataframe = pd.read_csv(path)

    required_columns = {
        "latitude",
        "longitude",
        "acq_date",
        "acq_time",
        "frp",
        "daynight",
    }

    missing = required_columns.difference(
        dataframe.columns
    )

    if missing:
        raise ValueError(
            f"Missing FIRMS columns: {sorted(missing)}"
        )

    imported = 0

    with SessionLocal() as db:
        for _, row in dataframe.iterrows():
            latitude = float(row["latitude"])
            longitude = float(row["longitude"])

            detected_at = parse_detected_at(row)

            firms_id = clean_value(
                row.get("id")
            )

            if firms_id is None:
                firms_id = (
                    f"{latitude:.6f}_"
                    f"{longitude:.6f}_"
                    f"{detected_at.isoformat()}"
                )

            values = {
                "firms_id": str(firms_id),
                "latitude": latitude,
                "longitude": longitude,
                "detected_at": detected_at,
                "acq_date": row["acq_date"],
                "satellite": clean_value(
                    row.get("satellite")
                ),
                "instrument": clean_value(
                    row.get("instrument")
                ),
                "source": clean_value(
                    row.get("source")
                ),
                "frp": clean_value(
                    row.get("frp")
                ),
                "confidence": clean_value(
                    row.get("confidence")
                ),
                "day_night": clean_value(
                    row.get("daynight")
                ),
                "brightness_ti4": clean_value(
                    row.get("bright_ti4")
                ),
                "brightness_ti5": clean_value(
                    row.get("bright_ti5")
                ),
            }

            statement = text(
                """
                INSERT INTO firms_detections (
                    firms_id,
                    latitude,
                    longitude,
                    detected_at,
                    acq_date,
                    satellite,
                    instrument,
                    source,
                    frp,
                    confidence,
                    day_night,
                    brightness_ti4,
                    brightness_ti5,
                    geom
                )
                VALUES (
                    :firms_id,
                    :latitude,
                    :longitude,
                    :detected_at,
                    :acq_date,
                    :satellite,
                    :instrument,
                    :source,
                    :frp,
                    :confidence,
                    :day_night,
                    :brightness_ti4,
                    :brightness_ti5,
                    ST_SetSRID(
                        ST_MakePoint(
                            :longitude,
                            :latitude
                        ),
                        4326
                    )::geography
                )
                ON CONFLICT (firms_id)
                DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    detected_at = EXCLUDED.detected_at,
                    acq_date = EXCLUDED.acq_date,
                    satellite = EXCLUDED.satellite,
                    instrument = EXCLUDED.instrument,
                    source = EXCLUDED.source,
                    frp = EXCLUDED.frp,
                    confidence = EXCLUDED.confidence,
                    day_night = EXCLUDED.day_night,
                    brightness_ti4 = EXCLUDED.brightness_ti4,
                    brightness_ti5 = EXCLUDED.brightness_ti5,
                    geom = EXCLUDED.geom
                """
            )

            db.execute(statement, values)
            imported += 1

        db.commit()

    return imported


if __name__ == "__main__":
    csv_file = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "data/firms_latest.csv"
    )

    count = import_firms_csv(csv_file)

    print(
        f"Imported or updated {count} FIRMS detections."
    )