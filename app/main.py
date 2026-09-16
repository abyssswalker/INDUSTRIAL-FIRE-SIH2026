from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from geoalchemy2.shape import to_shape
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud

app = FastAPI(
    title="Industrial Fire SIH2026 API",
    description="NASA FIRMS + Bhuvan + PostGIS powered fire analytics",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Industrial Fire API is running. Open /docs for Swagger."}

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