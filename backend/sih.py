from fastapi import FastAPI

app = FastAPI()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS setup — frontend ko permission deta hai API se baat karne ki
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allowing everyone for the prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fake data — jaisa real data baad mein aayega
fake_hotspots = [
    {
        "id": "hs_001",
        "latitude": 21.1458,
        "longitude": 79.0882,
        "location_name": "Nagpur Industrial Belt",
        "classification": "Industrial",       # ya "Transient"
        "confidence": 0.92,
        "recurrence_count": 34,
        "nearest_osm_feature": "Steel Plant, Nagpur",
        "distance_to_osm_m": 340,
        "last_detected": "2026-08-20"
    },
    {
        "id": "hs_002",
        "latitude": 21.2000,
        "longitude": 79.1200,
        "location_name": "Forest Belt, Seoni",
        "classification": "Transient",
        "confidence": 0.78,
        "recurrence_count": 2,
        "nearest_osm_feature": None,
        "distance_to_osm_m": None,
        "last_detected": "2026-07-15"
    }
]

@app.get("/hello")
def say_hello():
    return {"message": "Hello, I am your fire detection API"}

@app.get("/hotspots")
def get_hotspots():
    return fake_hotspots

@app.get("/hotspots/{hotspot_id}")
def get_hotspot_detail(hotspot_id: str):
    for spot in fake_hotspots:
        if spot["id"] == hotspot_id:
            return spot
    return {"error": "Hotspot not found"}

@app.get("/stats")
def get_stats():
    industrial_count = sum(1 for h in fake_hotspots if h["classification"] == "Industrial")
    transient_count = sum(1 for h in fake_hotspots if h["classification"] == "Transient")
    return {
        "total_hotspots": len(fake_hotspots),
        "industrial_count": industrial_count,
        "transient_count": transient_count
    }