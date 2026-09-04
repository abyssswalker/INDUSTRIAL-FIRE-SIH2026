from fastapi import FastAPI , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd


main_dir = Path(__file__).resolve().parent.parent
data_dir = main_dir /'DataBase'
cluster_dir = data_dir /'Cluster'

app = FastAPI()

# CORS setup — frontend ko permission deta hai API se baat karne ki
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allowing everyone for the prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Real data
df = pd.read_csv(cluster_dir/'cluster_labeled.csv')

hotspots = []
for _, row in df.iterrows():
    hotspots.append(
        {
            "id": str(row["cluster_id"]),
            "lat": row["centroid_lat"],
            "lon": row["centroid_lon"],
            "classification": row["label"],  # industrial / wildfire / uncertain
            "confidence": None,  # not available until XGBoost stretch goal
            "recurrence_count": int(row["detection_count"]),
            "frp_variance": row["frp_cv"],
            "day_night_ratio": row["daynight_ratio"],
            "nearest_industrial_type": (
                row["nearest_industrial_type"]
                if pd.notna(row["nearest_industrial_type"])
                else None
            ),
            "nearest_industrial_distance_m": (
                row["nearest_industrial_distance_m"]
                if pd.notna(row["nearest_industrial_distance_m"])
                else None
            ),
        }
    )


@app.get("/hello")
def say_hello():
    return {"message": "Hello, I am your fire detection API"}

@app.get("/hotspots")
def get_hotspots():
    return hotspots


@app.get("/hotspots/{hotspot_id}")
def get_hotspot_detail(hotspot_id: str):
    for spot in hotspots:
        if spot["id"] == hotspot_id:
            return spot
    raise HTTPException(status_code=404, detail="Hotspot not found")


@app.get("/stats")
def get_stats():
    industrial_count = sum(1 for h in hotspots if h["classification"] == "industrial")
    wildfire_count = sum(1 for h in hotspots if h["classification"] == "wildfire")
    uncertain_count = sum(1 for h in hotspots if h["classification"] == "uncertain")
    return {
        "total_hotspots": len(hotspots),
        "industrial_count": industrial_count,
        "wildfire_count": wildfire_count,
        "uncertain_count": uncertain_count,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
