from sqlalchemy.orm import Session

from app.models import ClusterSummary


def get_hotspots(db: Session):
    return db.query(ClusterSummary).order_by(ClusterSummary.cluster_id).all()


def get_hotspot(db: Session, cluster_id: int):
    return db.query(ClusterSummary).filter(ClusterSummary.cluster_id == cluster_id).first()


def get_stats(db: Session):
    total = db.query(ClusterSummary).count()
    industrial = db.query(ClusterSummary).filter(ClusterSummary.label == "industrial").count()
    wildfire = db.query(ClusterSummary).filter(ClusterSummary.label == "wildfire").count()
    uncertain = db.query(ClusterSummary).filter(ClusterSummary.label == "uncertain").count()
    return {
        "total_clusters": total,
        "industrial_clusters": industrial,
        "wildfire_clusters": wildfire,
        "uncertain_clusters": uncertain,
    }