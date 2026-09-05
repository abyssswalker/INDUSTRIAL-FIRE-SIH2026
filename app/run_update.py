#runs the whole update process
from app.build_hotspots import build_hotspots
from app.import_firms import import_firms_csv
from app.import_osm import import_osm_geojson


def main() -> None:
    firms_count = import_firms_csv(
        "data/firms_latest.csv"
    )

    osm_count = import_osm_geojson(
        "data/osm_features.geojson"
    )

    hotspot_count = build_hotspots()

    print(
        "Pipeline completed successfully."
    )

    print(
        f"FIRMS rows imported: {firms_count}"
    )

    print(
        f"OSM features imported: {osm_count}"
    )

    print(
        f"Hotspot clusters updated: {hotspot_count}"
    )


if __name__ == "__main__":
    main()