# run_pipeline.py
"""Canonical GeoContext-AI historical pipeline.

The previous staged clustering and rule-based classifier are no longer part
of the execution path. This runner prepares FIRMS data for the new anomaly
engine and persists discovered ghost-zone baselines as a portable CSV.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from .data_pull_api import pull_data
    from .ml_pipeline import GeoContextAnomalyEngine
except ImportError:  # Supports: python ml/run_pipeline.py
    from data_pull_api import pull_data
    from ml_pipeline import GeoContextAnomalyEngine


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "DataBase"
DEFAULT_INPUT = DATA_DIR / "Raw.csv"
DEFAULT_OUTPUT = DATA_DIR / "Cluster" / "ghost_zone_baselines.csv"


def prepare_firms_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Normalize FIRMS column names without applying inference filters.

    FIRMS exports commonly use ``daynight`` while the engine's public schema
    uses ``DayNight``. Filtering is intentionally left to the engine so the
    same rules are applied consistently in every caller.
    """
    normalized = dataframe.copy()
    if "DayNight" not in normalized.columns and "daynight" in normalized.columns:
        normalized = normalized.rename(columns={"daynight": "DayNight"})

    required = {"latitude", "longitude", "frp", "confidence", "DayNight"}
    missing = required.difference(normalized.columns)
    if missing:
        raise ValueError(f"FIRMS data is missing columns: {sorted(missing)}")
    return normalized


def run_historical_pipeline(
    input_path: str | Path = DEFAULT_INPUT,
    output_path: str | Path = DEFAULT_OUTPUT,
    *,
    download: bool = False,
) -> pd.DataFrame:
    """Discover ghost zones from FIRMS history and save their baselines.

    Args:
        input_path: FIRMS CSV used when ``download`` is false.
        output_path: CSV destination for discovered zone baselines.
        download: Pull fresh FIRMS data before processing.

    Returns:
        The GeoDataFrame produced by ``discover_ghost_zones``.
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    if download:
        print("Downloading FIRMS data...")
        pull_data()
        input_file = DEFAULT_INPUT

    if not input_file.is_absolute():
        input_file = PROJECT_DIR / input_file
    if not input_file.exists():
        raise FileNotFoundError(f"FIRMS input file does not exist: {input_file}")

    print(f"Reading FIRMS data from {input_file}")
    historical_data = prepare_firms_data(pd.read_csv(input_file, low_memory=False))
    zones = GeoContextAnomalyEngine().discover_ghost_zones(historical_data)

    if not output_file.is_absolute():
        output_file = PROJECT_DIR / output_file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    export = zones.drop(columns=["geometry"], errors="ignore").rename(
        columns={
            "cluster_id": "zone_id",
            "latitude": "centroid_lat",
            "longitude": "centroid_lon",
        }
    )
    export.to_csv(output_file, index=False)
    print(f"Discovered {len(zones)} ghost zones")
    print(f"Saved zone baselines to {output_file}")
    return zones


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="FIRMS CSV path; defaults to DataBase/Raw.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Ghost-zone baseline CSV path",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download fresh FIRMS data before running the historical phase",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_historical_pipeline(arguments.input, arguments.output, download=arguments.download)
