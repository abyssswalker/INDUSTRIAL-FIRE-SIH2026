"""Historical ghost-zone discovery and live anomaly scoring."""

from __future__ import annotations

import asyncio
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
from sklearn.cluster import DBSCAN


class GeoContextAnomalyEngine:
    EARTH_RADIUS_METERS = 6_371_000.0
    GHOST_ZONE_RADIUS_METERS = 500.0
    MIN_SAMPLES = 30
    DISASTER_Z_SCORE = 3.0
    _HISTORICAL_COLUMNS = {"latitude", "longitude", "frp", "confidence", "DayNight"}
    _LIVE_COLUMNS = _HISTORICAL_COLUMNS
    _ZONE_BASELINE_COLUMNS = {"log_mean", "log_std"}

    def discover_ghost_zones(self, historical_df: pd.DataFrame) -> gpd.GeoDataFrame:
        self._require_columns(historical_df, self._HISTORICAL_COLUMNS, "historical_df")
        detections = self._keep_valid_fire_rows(
            historical_df.loc[
                historical_df["confidence"].astype("string").str.lower().ne("l")
                & historical_df["DayNight"].astype("string").str.upper().eq("N")
            ].copy()
        )

        result_columns = [
            "cluster_id",
            "latitude",
            "longitude",
            "log_mean",
            "log_std",
            "detection_count",
            "geometry",
        ]
        if detections.empty:
            return gpd.GeoDataFrame(columns=result_columns, geometry="geometry", crs="EPSG:4326")

        model = DBSCAN(
            eps=self.GHOST_ZONE_RADIUS_METERS / self.EARTH_RADIUS_METERS,
            min_samples=self.MIN_SAMPLES,
            metric="haversine",
            algorithm="ball_tree",
        )
        detections["cluster_id"] = model.fit_predict(np.radians(detections[["latitude", "longitude"]].to_numpy(dtype=float)))
        clustered = detections[detections["cluster_id"] != -1].copy()
        if clustered.empty:
            return gpd.GeoDataFrame(columns=result_columns, geometry="geometry", crs="EPSG:4326")

        clustered["log_frp"] = np.log(clustered["frp"].astype(float))
        zones = (
            clustered.groupby("cluster_id", as_index=False)
            .agg(
                latitude=("latitude", "mean"),
                longitude=("longitude", "mean"),
                log_mean=("log_frp", "mean"),
                log_std=("log_frp", lambda s: s.std(ddof=0)),
                detection_count=("cluster_id", "size"),
            )
        )
        zones["geometry"] = [
            Point(lon, lat) for lat, lon in zip(zones["latitude"], zones["longitude"])
        ]
        return gpd.GeoDataFrame(zones[result_columns], geometry="geometry", crs="EPSG:4326")

    def calculate_live_anomaly(self, live_point_frp: float, zone_log_mean: float, zone_log_std: float) -> dict[str, Any]:
        live_frp = self._finite_float(live_point_frp, "live_point_frp")
        log_mean = self._finite_float(zone_log_mean, "zone_log_mean")
        log_std = self._finite_float(zone_log_std, "zone_log_std")
        if log_std < 0:
            raise ValueError("zone_log_std must be non-negative")

        diff = float(np.log(live_frp)) - log_mean
        z_score = 0.0 if log_std == 0 and diff == 0 else (diff / log_std if log_std else float(np.copysign(np.inf, diff)))
        return {"z_score": float(z_score), "is_disaster": bool(z_score > self.DISASTER_Z_SCORE)}

    async def async_inference_wrapper(self, live_points_df: pd.DataFrame, zones_data: pd.DataFrame | gpd.GeoDataFrame) -> pd.DataFrame:
        self._require_columns(live_points_df, self._LIVE_COLUMNS, "live_points_df")
        self._require_columns(zones_data, self._ZONE_BASELINE_COLUMNS, "zones_data")
        return await asyncio.to_thread(self._run_batch_inference, live_points_df.copy(), zones_data.copy())

    def _run_batch_inference(self, live_points_df: pd.DataFrame, zones_data: pd.DataFrame | gpd.GeoDataFrame) -> pd.DataFrame:
        live_points = self._prepare_live_points(live_points_df)
        zones = zones_data.copy()

        if "zone_id" not in live_points.columns:
            live_points = self._assign_zones_spatially(live_points, zones)
        elif "zone_id" not in zones.columns:
            raise ValueError("zones_data must contain 'zone_id' when live_points_df has zone_id")
        if "zone_id" not in zones.columns:
            raise ValueError("zones_data must contain 'zone_id' for spatially matched inference results")

        baselines = zones[["zone_id", "log_mean", "log_std"]].drop_duplicates("zone_id")
        results = live_points.merge(baselines, on="zone_id", how="left", validate="many_to_one")

        missing = results["log_mean"].isna() | results["log_std"].isna()
        if missing.any():
            raise ValueError(f"No complete baseline found for zone IDs: {results.loc[missing, 'zone_id'].tolist()}")

        anomaly = results.apply(
            lambda row: self.calculate_live_anomaly(row["frp"], row["log_mean"], row["log_std"]),
            axis=1,
            result_type="expand",
        )
        results["z_score"] = anomaly["z_score"]
        results["is_disaster"] = anomaly["is_disaster"].astype(bool)
        return results

    def _assign_zones_spatially(self, live_points_df: pd.DataFrame, zones_data: pd.DataFrame | gpd.GeoDataFrame) -> pd.DataFrame:
        if not isinstance(zones_data, gpd.GeoDataFrame) or zones_data.geometry is None:
            raise ValueError("zones_data must be a GeoDataFrame with polygon geometry when live points have no zone_id")
        if zones_data.crs is None:
            raise ValueError("zones_data must define a CRS for spatial inference")

        live_geo = gpd.GeoDataFrame(
            live_points_df,
            geometry=[Point(lon, lat) for lat, lon in zip(live_points_df["latitude"], live_points_df["longitude"])],
            crs="EPSG:4326",
        ).to_crs(zones_data.crs)

        zone_columns = ["zone_id", "geometry"]
        missing_columns = set(zone_columns) - set(zones_data.columns)
        if missing_columns:
            raise ValueError(f"zones_data is missing columns: {sorted(missing_columns)}")

        joined = gpd.sjoin(live_geo, zones_data[zone_columns], how="left", predicate="within")
        return pd.DataFrame(joined.drop(columns=["geometry", "index_right"], errors="ignore"))

    @staticmethod
    def _prepare_live_points(live_points_df: pd.DataFrame) -> pd.DataFrame:
        live_points = live_points_df.copy()
        mask = (
            live_points["confidence"].astype("string").str.lower().isin({"n", "h"})
            & live_points["DayNight"].astype("string").str.upper().isin({"D", "N"})
        )
        live_points = GeoContextAnomalyEngine._keep_valid_fire_rows(live_points.loc[mask].copy())
        if live_points.empty:
            raise ValueError("live_points_df contains no valid D/N points with nominal or high confidence and positive FRP")
        return live_points

    @staticmethod
    def _keep_valid_fire_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
        numeric = dataframe[["latitude", "longitude", "frp"]].apply(pd.to_numeric, errors="coerce").astype(float)
        valid = numeric["latitude"].between(-90, 90) & numeric["longitude"].between(-180, 180) & np.isfinite(numeric["frp"].to_numpy()) & (numeric["frp"] > 0)
        cleaned = dataframe.loc[valid].copy()
        cleaned[["latitude", "longitude", "frp"]] = numeric.loc[valid]
        return cleaned

    @staticmethod
    def _require_columns(dataframe: pd.DataFrame, required: set[str], name: str) -> None:
        missing = required - set(dataframe.columns)
        if missing:
            raise ValueError(f"{name} is missing columns: {sorted(missing)}")

    @staticmethod
    def _finite_float(value: float, name: str) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be a finite number") from exc
        if not np.isfinite(number):
            raise ValueError(f"{name} must be a finite number")
        if name == "live_point_frp" and number <= 0:
            raise ValueError("live_point_frp must be greater than zero")
        return number
