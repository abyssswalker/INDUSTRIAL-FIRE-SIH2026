document.addEventListener("DOMContentLoaded", async () => {
  const mapContainer = document.getElementById("map");
  const loadingEl = document.getElementById("loading");

  // Initialize map centered on Chhattisgarh
  const map = L.map("map", {
    center: [21.5, 82.0],
    zoom: 7,
    zoomControl: true,
  });

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  const hotspotsUrl = window.APP_CONFIG?.hotspotsUrl || "/hotspots";

  try {
    const res = await fetch(hotspotsUrl);
    if (!res.ok) {
      throw new Error(`Failed to load hotspots: ${res.status} ${res.statusText}`);
    }

    const clusters = await res.json();

    if (!Array.isArray(clusters) || clusters.length === 0) {
      loadingEl.textContent = "No hotspots found in the database.";
      return;
    }

    // Remove loading overlay once we have data
    loadingEl.remove();

    const bounds = [];

    clusters.forEach((cluster) => {
      const lat = cluster.centroid_lat;
      const lon = cluster.centroid_lon;

      if (lat == null || lon == null) {
        return;
      }

      const marker = L.marker([lat, lon]).addTo(map);
      bounds.push([lat, lon]);

      const clusterId = cluster.cluster_id ?? "N/A";
      const label = cluster.label ?? "uncertain";
      const detections = cluster.detection_count ?? "N/A";
      const distanceM = cluster.nearest_industrial_distance_m;
      const industrialType = cluster.nearest_industrial_type;
      const frpMean = cluster.frp_mean;
      const recurrence = cluster.recurrence_rate;
      const industrialScore = cluster.industrial_score;
      const wildfireScore = cluster.wildfire_score;

      let popupLines = [
        `<b>Cluster ${clusterId}</b>`,
        `<b>Label:</b> ${label}`,
        `<b>Detections:</b> ${detections}`,
      ];

      if (distanceM != null) {
        popupLines.push(`<b>Nearest industrial distance:</b> ${distanceM.toFixed(1)} m`);
      }
      if (industrialType) {
        popupLines.push(`<b>Nearest industrial type:</b> ${industrialType}`);
      }
      if (frpMean != null) {
        popupLines.push(`<b>FRP mean:</b> ${frpMean.toFixed(2)}`);
      }
      if (recurrence != null) {
        popupLines.push(`<b>Recurrence rate:</b> ${recurrence.toFixed(2)}`);
      }
      if (industrialScore != null || wildfireScore != null) {
        const ind = industrialScore != null ? industrialScore.toFixed(2) : "N/A";
        const wild = wildfireScore != null ? wildfireScore.toFixed(2) : "N/A";
        popupLines.push(`<b>Industrial score:</b> ${ind}`);
        popupLines.push(`<b>Wildfire score:</b> ${wild}`);
      }

      const popupContent = popupLines.join("<br>");
      marker.bindPopup(popupContent);
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  } catch (err) {
    console.error(err);
    loadingEl.textContent = "Failed to load hotspots. Check console for details.";
  }
});