import pandas as pd
from pathlib import Path
from pyproj import Transformer
from sklearn.cluster import DBSCAN

main_dir = Path(__file__).resolve().parent
data_dir = main_dir.parent/'DataBase'

fires = pd.read_csv(data_dir / "chatisgarh_clean.csv")

#  coordinate conversion logic

transformer = Transformer.from_crs("EPSG:4326", "EPSG:32645", always_xy=True)

fires["x_m"], fires["y_m"] = transformer.transform(fires["longitude"].values, fires["latitude"].values)


#                                      main clustering


coords = fires[["x_m", "y_m"]].values

model = DBSCAN(eps=500, min_samples=5)
fires["cluster_id"] = model.fit_predict(coords)


#                                          test


n_clusters = fires["cluster_id"].nunique() - (
    1 if -1 in fires["cluster_id"].values else 0
)
n_noise = (fires["cluster_id"] == -1).sum()

print(f"Clusters found: {n_clusters}")
print(f"Noise points: {n_noise} out of {len(fires)}")
print(fires["cluster_id"].value_counts().head(10))


#                       get centroid (average lat/lon) of each cluster


cluster_summary = (
    fires
    .groupby("cluster_id")
    .agg(
        detection_count=("cluster_id", "size"),
        centroid_lat=("latitude", "mean"),
        centroid_lon=("longitude", "mean"),
    )
    .sort_values("detection_count", ascending=False)
)

print(cluster_summary.head(10))



clustered = fires.copy()


clustered = clustered.merge(
    cluster_summary[["centroid_lat", "centroid_lon", "detection_count"]],
    on="cluster_id",
    how="left",
)

cluster_dir = data_dir/'Cluster'
clustered.to_csv(cluster_dir/'Clusters.csv',index=False)
