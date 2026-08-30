import pandas as pd
import pyproj as pyp
import time
from datetime import date,timedelta
from pathlib import Path



# pulling data from api

Map_key = "ef82f0c7ed91d8469d3ae4f2fa005016"
SourceSP = "VIIRS_NOAA20_SP"   # for older data (2 months+ older)
SourceNRT = "VIIRS_NOAA20_NRT"  # for new data within 2 months 
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

