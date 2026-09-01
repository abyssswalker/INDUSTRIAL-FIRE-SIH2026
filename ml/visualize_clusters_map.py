"""
visualize_clusters_map.py

Plots every labeled fire cluster on an interactive map, color-coded by label:
    red    = industrial
    blue   = wildfire
    gray   = uncertain

Click any point to see its stats (recurrence_rate, frp_cv, distance to
nearest industrial feature, daynight_ratio) — this is the "eyeball 10-20
clusters" step the original plan called for, so we tune thresholds based
on what actually looks right on the map, not guesswork.

Input:  DataBase/Cluster/cluster_labeled.csv
Output: DataBase/Cluster/clusters_map.html  (open this in your browser)

If folium isn't installed yet, run this first:
    pip install folium
"""

from pathlib import Path
import pandas as pd
import folium

main_dir = Path(__file__).resolve().parent
data_dir = main_dir.parent / "DataBase"

input_path = data_dir / "Cluster" / "cluster_labeled.csv"
output_path = data_dir / "Cluster" / "clusters_map.html"

df = pd.read_csv(input_path)

# center the map roughly on Chhattisgarh
center_lat = df["centroid_lat"].mean()
center_lon = df["centroid_lon"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="OpenStreetMap")

color_map = {
    "industrial": "red",
    "wildfire": "blue",
    "uncertain": "gray",
}

# add a few known real industrial hubs as reference markers (green stars)
# so you can visually check if "industrial" (red) points cluster near them
reference_hubs = {
    "Bhilai (steel)": (21.2094, 81.3509),
    "Raipur": (21.2514, 81.6296),
    "Korba (power/coal)": (22.3595, 82.6805),
    "Raigarh (steel/power)": (21.8974, 83.3950),
    "Durg": (21.1904, 81.2849),
    "Bilaspur": (22.0797, 82.1409),
}
for name, (lat, lon) in reference_hubs.items():
    folium.Marker(
        location=[lat, lon],
        popup=f"REFERENCE HUB: {name}",
        icon=folium.Icon(color="green", icon="star"),
    ).add_to(m)

for _, row in df.iterrows():
    label = row["label"]
    popup_text = (
        f"<b>Cluster {row['cluster_id']}</b><br>"
        f"Label: <b>{label}</b><br>"
        f"Recurrence rate: {row['recurrence_rate']:.2f}<br>"
        f"FRP CV: {row['frp_cv']:.2f}<br>"
        f"Distance to industrial: {row['nearest_industrial_distance_m']:.0f} m<br>"
        f"Day/night ratio: {row['daynight_ratio']:.2f}<br>"
        f"Detection count: {row['detection_count']}"
    )
    folium.CircleMarker(
        location=[row["centroid_lat"], row["centroid_lon"]],
        radius=5,
        color=color_map.get(label, "black"),
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(popup_text, max_width=250),
    ).add_to(m)

m.save(str(output_path))
print(f"Map saved to {output_path}")
print("Open this file in your browser (double-click it in File Explorer) to view it.")
