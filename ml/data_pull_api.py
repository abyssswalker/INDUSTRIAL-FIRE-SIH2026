import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from app.config import NASA_FIRMS_API_KEY, NASA_FIRMS_SENSOR


def _firms_url(map_key: str, source: str, area: str, day_range: int, current_date: date) -> str:
    return (
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key}/{source}/{area}/"
        f"{day_range}/{current_date}"
    )


def fetch_recent_firms_last_12_hours() -> pd.DataFrame:
    """Fetch the latest available FIRMS detections for the last 12 hours."""
    map_key = NASA_FIRMS_API_KEY
    source_nrt = NASA_FIRMS_SENSOR
    area = "80.15,17.75,84.25,24.10"

    frames = []
    for offset in range(0, 3):
        current_date = date.today() - timedelta(days=offset)
        url = _firms_url(map_key, source_nrt, area, day_range=1, current_date=current_date)
        try:
            df = pd.read_csv(url)
        except Exception:
            continue
        if not df.empty:
            frames.append(df)
        time.sleep(1)

    if not frames:
        return pd.DataFrame(columns=["latitude", "longitude", "frp", "confidence", "daynight", "acq_DateTime"])

    recent = pd.concat(frames, ignore_index=True)
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(hours=12)
    if "acq_DateTime" in recent.columns:
        recent["acq_DateTime"] = pd.to_datetime(
            recent["acq_DateTime"], errors="coerce", utc=True
        )
        recent = recent[recent["acq_DateTime"] >= cutoff].copy()
    elif "acq_time" in recent.columns:
        recent["acq_time"] = pd.to_datetime(
            recent["acq_time"], errors="coerce", utc=True
        )
        recent = recent[recent["acq_time"] >= cutoff].copy()

    if "daynight" in recent.columns and "DayNight" not in recent.columns:
        recent = recent.rename(columns={"daynight": "DayNight"})
    if "acq_time" in recent.columns and "acq_DateTime" not in recent.columns:
        recent = recent.rename(columns={"acq_time": "acq_DateTime"})

    return recent


def pull_data():
# pulling data from api

 Map_key = NASA_FIRMS_API_KEY
 SourceSP = "VIIRS_NOAA20_SP"   # for older data (2 months+ older)
 SourceNRT = NASA_FIRMS_SENSOR  # for new data within 2 months
 Area = "80.15,17.75,84.25,24.10"  # Korba, Chhattisgarh

 MAIN_dir = Path(__file__).resolve().parent.parent
 data_dir = MAIN_dir/"DataBase"
 output_path = data_dir/"Raw.csv"








#                                             10 months data 

 all_data_SP = []
 day_range = 5
 start_date_SP = date.today() - timedelta(days=365)
 end_date_SP = date.today() - timedelta(days=60)
 current_SP = start_date_SP


 while current_SP <= end_date_SP :
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{Map_key}/{SourceSP}/{Area}/{day_range}/{current_SP}"
    df = pd.read_csv(url)
    all_data_SP.append(df)
    current_SP += timedelta(days= 10)
    time.sleep(1)

 fires_SP = pd.concat(all_data_SP, ignore_index=True)




#                                             2 months data                          


 all_data_NRT = []
 start_date_NRT = date.today() - timedelta(days=60)
 end_date_NRT = date.today()
 current_NRT = start_date_NRT

 while current_NRT <= end_date_NRT:
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{Map_key}/{SourceNRT}/{Area}/{day_range}/{current_NRT}"
    df = pd.read_csv(url)
    all_data_NRT.append(df)
    current_NRT += timedelta(days=day_range)
    time.sleep(1)

 fires_NRT = pd.concat(all_data_NRT,ignore_index=True)

 Fire = pd.concat([fires_NRT,fires_SP],ignore_index=True)

 Fire.to_csv(output_path,index = False)


if __name__ == '__main__':
    pull_data()