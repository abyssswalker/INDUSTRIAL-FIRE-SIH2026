from typing import List, Tuple, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import to_shape

from app.models import Fire, IndustrialArea, ClusterBaseline

async def list_current_fires(db: AsyncSession) -> List[Fire]:
    stmt = select(Fire).order_by(Fire.acq_timestamptz.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_fires_near_industrial(
    db: AsyncSession,
    distance_m: float = 500,
) -> List[Tuple[Fire, IndustrialArea]]:
    stmt = select(Fire, IndustrialArea).where(
        func.ST_DWithin(
            func.geography(Fire.geom),
            func.geography(IndustrialArea.geom),
            distance_m,
        )
    )
    result = await db.execute(stmt)
    return list(result.all())

async def compute_zscore_for_fire(
    db: AsyncSession,
    fire: Fire,
) -> Optional[float]:
    # Find nearest cluster by centroid
    stmt = select(ClusterBaseline).order_by(
        func.ST_Distance(
            func.geography(fire.geom),
            func.geography(ClusterBaseline.centroid_geom),
        )
    ).limit(1)
    cluster = await db.scalar(stmt)
    if not cluster or not cluster.frp_std or cluster.frp_std == 0:
        return None
    z = (float(fire.frp) - float(cluster.frp_mean)) / float(cluster.frp_std)
    return z

async def get_cluster_baselines(db: AsyncSession) -> List[ClusterBaseline]:
    stmt = select(ClusterBaseline)
    result = await db.execute(stmt)
    return list(result.scalars().all())