import pandas as pd
from pathlib import Path
from pyproj import Transformer
from sklearn.cluster import DBSCAN
def clustering():
 main_dir = Path(__file__).resolve().parent
 data_dir = main_dir.parent/'DataBase'

 fires = pd.read_csv(data_dir / "chatisgarh_clean.csv")

#  coordinate conversion logic

 transformer = Transformer.from_crs("EPSG:4326", "EPSG:32644", always_xy=True)

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
    fires[fires["cluster_id"] != -1]
    .groupby("cluster_id")
    .agg(
        detection_count=("cluster_id", "size"),
        centroid_lat=("latitude", "mean"),
        centroid_lon=("longitude", "mean"),
    )
    .sort_values("detection_count", ascending=False)
    .reset_index()
 )

 print(cluster_summary.head(10))


 clustered = fires.copy()


 clustered = clustered.merge(
    cluster_summary[["cluster_id", "centroid_lat", "centroid_lon", "detection_count"]],
    on="cluster_id",
    how="left",
 )
 clustered["centroid_lat"] = clustered["centroid_lat"].fillna(clustered["latitude"])
 clustered["centroid_lon"] = clustered["centroid_lon"].fillna(clustered["longitude"])
 clustered["detection_count"] = clustered["detection_count"].fillna(1).astype(int)

 cluster_dir = data_dir/'Cluster'
 cluster_dir.mkdir(parents=True, exist_ok=True)
 clustered.to_csv(cluster_dir/'Clusters.csv',index=False)
 clustered[['cluster_id','centroid_lat','centroid_lon']].to_csv(data_dir/'osm'/'cluster_csv_for_osm.csv',index =False)


if __name__ == '__main__':
    clustering()