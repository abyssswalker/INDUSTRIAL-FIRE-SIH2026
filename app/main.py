from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.crud import get_hotspot, get_hotspots, get_stats
from app.database import get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={})


@app.get("/map", response_class=HTMLResponse)
def map_page(request: Request):
    return templates.TemplateResponse(request=request, name="map.html", context={})


@app.get("/hotspots")
def read_hotspots(db: Session = Depends(get_db)):
    return get_hotspots(db)


@app.get("/hotspots/{cluster_id}")
def read_hotspot(cluster_id: int, db: Session = Depends(get_db)):
    hotspot = get_hotspot(db, cluster_id)
    if not hotspot:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return hotspot


@app.get("/stats")
def read_stats(db: Session = Depends(get_db)):
    return get_stats(db)