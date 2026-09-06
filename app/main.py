from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.crud import get_hotspot, get_hotspots, get_stats
from app.database import get_db
from app.schemas import HotspotOut

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    with open("templates/map.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/hotspots", response_model=list[HotspotOut])
def read_hotspots(db: Session = Depends(get_db)):
    return get_hotspots(db)

@app.get("/hotspots/{cluster_id}", response_model=HotspotOut)
def read_hotspot(cluster_id: int, db: Session = Depends(get_db)):
    hotspot = get_hotspot(db, cluster_id)
    if not hotspot:
        raise HTTPException(status_code=404, detail="Hotspot not found")
    return hotspot

@app.get("/stats")
def read_stats(db: Session = Depends(get_db)):
    return get_stats(db)