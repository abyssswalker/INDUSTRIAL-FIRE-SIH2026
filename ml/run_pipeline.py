# run_pipeline.py
from cluster import clustering
from Data_Cleaning import data_clean
from data_pull_api import pull_data


def run_pipeline():
    print("Step 1/4: Pulling FIRMS data...")
    pull_data()

    print("Step 2/4: Cleaning...")
    data_clean()

    print("Step 3/4: Clustering...")
    clustering()

   

    print("Pipeline complete.")


if __name__ == "__main__":
    run_pipeline()
