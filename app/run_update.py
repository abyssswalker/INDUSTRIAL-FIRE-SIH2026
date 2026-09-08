from pathlib import Path
from app.import_firms import import_clusters_csv

BASE_DIR = Path(__file__).resolve().parent.parent

def main() -> None:
    clusters_file = BASE_DIR / "Clusters.csv"
    count = import_clusters_csv(str(clusters_file))
    print(f"Imported {count} rows from Clusters.csv")

if __name__ == "__main__":
    main()