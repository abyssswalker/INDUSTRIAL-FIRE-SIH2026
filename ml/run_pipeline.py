# run_pipeline.py
from cluster import clustering
from Data_Cleaning import data_clean
from data_pull_api import pull_data
from distance_calculation import match_osm_distances


def run_pipeline():
    print("Step 1/5: Pulling FIRMS data...")
    pull_data()

    print("Step 2/5: Cleaning...")
    data_clean()

    print("Step 3/5: Clustering...")
    clustering()

    print("step 4/5: finding nearest osm")
    match_osm_distances()

    print("Pipeline complete.")


if __name__ == "__main__":
    run_pipeline()
