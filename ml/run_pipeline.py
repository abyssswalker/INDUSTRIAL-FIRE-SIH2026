# run_pipeline.py
from cluster import clustering
from MlRework.Data_Cleaning import data_clean
from data_pull_api import pull_data
from distance_calculation import match_osm_distances
import pandas as pd


def run_pipeline():
    print("Step 1/5: Pulling FIRMS data...")
    df_1 = pull_data()

    print("Step 2/5: Cleaning...")
    df_2 = data_clean(df_1)
    

    

    print("step 4/5: finding nearest osm")
    match_osm_distances()

    print("Pipeline complete.")


if __name__ == "__main__":
    run_pipeline()
