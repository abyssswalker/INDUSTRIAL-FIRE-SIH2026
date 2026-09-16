import pandas as pd
from pathlib import Path
import numpy as np

def data_clean():
    MAIN_dir = Path(__file__).resolve().parent.parent
    data_dir = MAIN_dir / "DataBase"

    fires = pd.read_csv(data_dir/"Raw.csv")

    fires = fires.drop_duplicates()

    fires = fires[fires['confidence'] != "l"]

    fires['acq_time'] = fires["acq_time"].astype(str).str.zfill(4)

    fires['acq_DateTime'] = pd.to_datetime( fires["acq_date"] + ' ' + fires["acq_time"].str[:2] + ':' + fires["acq_time"].str[2:])
    fires[fires['frp'] > 0].copy()

    fires["log_frp"] = np.log(fires["frp"])
    fires['daynight'] = fires['daynight'].astype(bool)

    columns_to_keep = [
        "latitude",
        "longitude",
        "acq_DateTime",
        "frp",
        "log_frp",
        "confidence",
        "bright_ti4",
        "bright_ti5","daynight"
    ]
    fires = fires[columns_to_keep]
    return fires


if __name__ == '__main__':
    print(data_clean().head())
    
