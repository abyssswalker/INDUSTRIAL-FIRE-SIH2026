from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models import Hotspot

def get_hotspots(db: Session):
    return db.execute(select(Hotspot).order_by(Hotspot.detection_count.desc())).scalars().all()

def get_hotspot(db: Session, cluster_id: int):
    return db.get(Hotspot, cluster_id)

def get_stats(db: Session):
    total = db.execute(select(func.count()).select_from(Hotspot)).scalar_one()
    industrial = db.execute(select(func.count()).select_from(Hotspot).where(Hotspot.classification == "industrial")).scalar_one()
    wildfire = db.execute(select(func.count()).select_from(Hotspot).where(Hotspot.classification == "wildfire")).scalar_one()
    uncertain = db.execute(select(func.count()).select_from(Hotspot).where(Hotspot.classification == "uncertain")).scalar_one()
    return {
        "total_hotspots": total,
        "industrial_count": industrial,
        "wildfire_count": wildfire,
        "uncertain_count": uncertain,
    }