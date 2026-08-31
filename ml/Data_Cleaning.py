import pandas as pd
from pathlib import Path

MAIN_dir = Path(__file__).resolve().parent.parent
data_dir = MAIN_dir / "DataBase"

fires = pd.read_csv(data_dir/"Raw.csv")

fires = fires.drop_duplicates()

fires = fires[fires['confidence'] != "l"]


fires['acq_time'] = fires["acq_time"].astype(str).str.zfill(4)

fires['acq_DateTime'] = pd.to_datetime( fires["acq_date"] + ' ' + fires["acq_time"].str[:2] + ':' + fires["acq_time"].str[2:])


fires = fires.drop(columns=['acq_date','acq_time','instrument','satellite'])

fires.to_csv(data_dir/'chatisgarh_clean.csv',index=False)


