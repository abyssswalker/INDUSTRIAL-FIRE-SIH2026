import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

NASA_FIRMS_API_KEY = os.getenv("NASA_FIRMS_API_KEY")

NASA_FIRMS_SENSOR = os.getenv(
    "NASA_FIRMS_SENSOR",
    "VIIRS_NOAA20_NRT",
)

NASA_FIRMS_DAYS = int(
    os.getenv("NASA_FIRMS_DAYS", "7")
)

DBSCAN_EPS_METERS = float(
    os.getenv("DBSCAN_EPS_METERS", "1000")
)

DBSCAN_MIN_SAMPLES = int(
    os.getenv("DBSCAN_MIN_SAMPLES", "2")
)

OSM_MATCH_DISTANCE_METERS = float(
    os.getenv("OSM_MATCH_DISTANCE_METERS", "5000")
)

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing from .env"
    )

if not NASA_FIRMS_API_KEY:
    raise RuntimeError(
        "NASA_FIRMS_API_KEY is missing from .env"
    )