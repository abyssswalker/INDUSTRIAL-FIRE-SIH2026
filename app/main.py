import math
from pathlib import Path

import geopandas as gpd
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from geoalchemy2.shape import to_shape
from sqlalchemy.ext.asyncio import AsyncSession
from shapely.geometry import Point

from app.database import get_db
from app import crud
from app.schemas import LiveInferenceRequest
from ml.ml_pipeline import GeoContextAnomalyEngine

BASE_DIR = Path(__file__).resolve().parent.parent
GHOST_ZONE_BASELINES = BASE_DIR / "DataBase" / "Cluster" / "ghost_zone_baselines.csv"

app = FastAPI(
    title="Industrial Fire SIH2026 API",
    description="NASA FIRMS + PostGIS powered fire analytics",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Industrial Fire API is running. Open /docs for Swagger."}


@app.post("/api/inference/live")
async def live_inference(
    payload: LiveInferenceRequest,
):
    """Score live FIRMS points against the generated ghost-zone CSV."""
    if not GHOST_ZONE_BASELINES.exists():
        raise HTTPException(
            status_code=503,
            detail="No ghost-zone baselines are available. Run ml/run_pipeline.py first.",
        )

    baselines = pd.read_csv(GHOST_ZONE_BASELINES)
    required = {"zone_id", "centroid_lat", "centroid_lon", "log_mean", "log_std"}
    missing = required.difference(baselines.columns)
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Ghost-zone baseline file is missing columns: {sorted(missing)}",
        )

    zones = gpd.GeoDataFrame(
        baselines,
        geometry=[
            Point(longitude, latitude)
            for latitude, longitude in zip(
                baselines["centroid_lat"], baselines["centroid_lon"]
            )
        ],
        crs="EPSG:4326",
    )
    zones = zones.to_crs("EPSG:32644")
    zones["geometry"] = zones.geometry.buffer(GeoContextAnomalyEngine.GHOST_ZONE_RADIUS_METERS)
    zones = zones.to_crs("EPSG:4326")

    live_points = pd.DataFrame([point.model_dump() for point in payload.points])
    results = await GeoContextAnomalyEngine().async_inference_wrapper(live_points, zones)
    records = results.to_dict(orient="records")
    for record in records:
        if not math.isfinite(float(record["z_score"])):
            record["z_score"] = None
    return {"results": records}

@app.get("/api/fires/current")
async def list_current_fires(db: AsyncSession = Depends(get_db)):
    fires = await crud.list_current_fires(db)
    features = []
    for f in fires:
        geom = to_shape(f.geom).__geo_interface__
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "firms_id": f.firms_id,
                "frp": float(f.frp) if f.frp is not None else None,
                "acq_time": f.acq_timestamptz.isoformat() if f.acq_timestamptz else None,
            },
        })
    return {"type": "FeatureCollection", "features": features}

@app.get("/api/fires/industrial-nearby")
async def fires_near_industrial(
    distance_m: float = 500,
    db: AsyncSession = Depends(get_db),
):
    rows = await crud.get_fires_near_industrial(db, distance_m)
    features = []
    for fire, ind in rows:
        geom = to_shape(fire.geom).__geo_interface__
        z = await crud.compute_zscore_for_fire(db, fire)
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "firms_id": fire.firms_id,
                "frp": float(fire.frp) if fire.frp else None,
                "zscore": z,
                "industrial_name": ind.name,
                "industrial_type": ind.feature_type,
                "source": ind.source,
            },
        })
    return {"type": "FeatureCollection", "features": features}

@app.get("/api/clusters")
async def list_clusters(db: AsyncSession = Depends(get_db)):
    clusters = await crud.get_cluster_baselines(db)
    out = []
    for c in clusters:
        geom = to_shape(c.centroid_geom).__geo_interface__ if c.centroid_geom else None
        out.append({
            "cluster_id": c.cluster_id,
            "label": c.label,
            "detection_count": c.detection_count,
            "frp_mean": float(c.frp_mean) if c.frp_mean else None,
            "frp_std": float(c.frp_std) if c.frp_std else None,
            "industrial_score": float(c.industrial_score) if c.industrial_score else None,
            "wildfire_score": float(c.wildfire_score) if c.wildfire_score else None,
            "geometry": geom,
        })
    return JSONResponse(content=out)

@app.get("/api/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    # Simple counts; extend as needed
    from sqlalchemy import select, func
    from app.models import Fire, ClusterBaseline

    total_fires = await db.scalar(select(func.count()).select_from(Fire))
    total_clusters = await db.scalar(select(func.count()).select_from(ClusterBaseline))
    industrial_clusters = await db.scalar(
        select(func.count()).select_from(ClusterBaseline).where(ClusterBaseline.label == "industrial")
    )
    return {
        "total_fires": total_fires,
        "total_clusters": total_clusters,
        "industrial_clusters": industrial_clusters,
    }