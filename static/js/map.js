document.addEventListener("DOMContentLoaded", async () => {
  const map = L.map("map", {
    center: [21.5, 82.0],
    zoom: 7,
    zoomControl: true,
  });

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  const loadingEl = document.getElementById("loading");

  const firesCurrentUrl = window.APP_CONFIG?.firesCurrentUrl || "/api/fires/current";
  const firesNearIndustrialUrl =
    window.APP_CONFIG?.firesNearIndustrialUrl || "/api/fires/industrial-nearby?distance_m=500";
  const clustersUrl = window.APP_CONFIG?.clustersUrl || "/api/clusters";

  const allBounds = [];

  // Layers
  const firesLayer = L.layerGroup().addTo(map);
  const nearIndustrialLayer = L.layerGroup().addTo(map);
  const clustersLayer = L.layerGroup().addTo(map);

  function addMarker(layer, lat, lon, popupHtml, color = "#1f77b4") {
    const marker = L.circleMarker([lat, lon], {
      radius: 6,
      color: "#333",
      weight: 1,
      fillColor: color,
      fillOpacity: 0.9,
    }).addTo(layer);

    marker.bindPopup(popupHtml);
    allBounds.push([lat, lon]);
  }

  try {
    // Load current fires
    const resFires = await fetch(firesCurrentUrl);
    if (!resFires.ok) throw new Error(`Fires current: ${resFires.status}`);
    const firesGeo = await resFires.json();

    (firesGeo.features || []).forEach((f) => {
      const coords = f.geometry?.coordinates;
      if (!coords) return;
      const [lon, lat] = coords;

      const props = f.properties || {};
      const firmsId = props.firms_id || "N/A";
      const frp = props.frp != null ? props.frp.toFixed(2) : "N/A";
      const acqTime = props.acq_time || "N/A";

      const popup = `
        <b>Fire</b><br>
        <b>FIRMS ID:</b> ${firmsId}<br>
        <b>FRP:</b> ${frp}<br>
        <b>Acquisition time:</b> ${acqTime}
      `;

      addMarker(firesLayer, lat, lon, popup, "#1f77b4");
    });

    // Load fires near industrial
    const resNear = await fetch(firesNearIndustrialUrl);
    if (!resNear.ok) throw new Error(`Fires near industrial: ${resNear.status}`);
    const nearGeo = await resNear.json();

    (nearGeo.features || []).forEach((f) => {
      const coords = f.geometry?.coordinates;
      if (!coords) return;
      const [lon, lat] = coords;

      const props = f.properties || {};
      const firmsId = props.firms_id || "N/A";
      const frp = props.frp != null ? props.frp.toFixed(2) : "N/A";
      const zscore = props.zscore != null ? props.zscore.toFixed(2) : "N/A";
      const indName = props.industrial_name || "N/A";
      const indType = props.industrial_type || "N/A";
      const source = props.source || "N/A";

      const popup = `
        <b>Fire near industrial</b><br>
        <b>FIRMS ID:</b> ${firmsId}<br>
        <b>FRP:</b> ${frp}<br>
        <b>Z‑score:</b> ${zscore}<br>
        <b>Industrial:</b> ${indName} (${indType})<br>
        <b>Source:</b> ${source}
      `;

      addMarker(nearIndustrialLayer, lat, lon, popup, "#d62728");
    });

    // Load clusters
    const resClusters = await fetch(clustersUrl);
    if (!resClusters.ok) throw new Error(`Clusters: ${resClusters.status}`);
    const clusters = await resClusters.json();

    (clusters || []).forEach((c) => {
      const geom = c.geometry;
      if (!geom || geom.type !== "Point") return;
      const [lon, lat] = geom.coordinates;

      const clusterId = c.cluster_id ?? "N/A";
      const label = c.label ?? "uncertain";
      const detections = c.detection_count ?? "N/A";
      const frpMean = c.frp_mean != null ? c.frp_mean.toFixed(2) : "N/A";
      const frpStd = c.frp_std != null ? c.frp_std.toFixed(2) : "N/A";
      const indScore = c.industrial_score != null ? c.industrial_score.toFixed(2) : "N/A";
      const wildScore = c.wildfire_score != null ? c.wildfire_score.toFixed(2) : "N/A";

      const popup = `
        <b>Cluster ${clusterId}</b><br>
        <b>Label:</b> ${label}<br>
        <b>Detections:</b> ${detections}<br>
        <b>FRP mean:</b> ${frpMean}<br>
        <b>FRP std:</b> ${frpStd}<br>
        <b>Industrial score:</b> ${indScore}<br>
        <b>Wildfire score:</b> ${wildScore}
      `;

      addMarker(clustersLayer, lat, lon, popup, "#2ca02c");
    });

    // Fit map to all markers
    if (allBounds.length > 0) {
      map.fitBounds(allBounds, { padding: [40, 40] });
    }
  } catch (err) {
    console.error(err);
    loadingEl.textContent = "Failed to load map data. Check console for details.";
    return;
  }

  loadingEl.remove();
});