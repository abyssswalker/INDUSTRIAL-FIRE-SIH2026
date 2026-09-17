/**
 * GeoContext-AI — Main Command Center Map Controller
 * Smart India Hackathon 2026
 */

function initCommandCenterMap() {
  // 1. Live Telemetry Clock (Formatted: Month Day, Year | HH:MM:SS UTC)
  const clockEl = document.getElementById("headerClock");
  function updateHeaderClock() {
    const now = new Date();
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const month = months[now.getUTCMonth()];
    const day = String(now.getUTCDate()).padStart(2, "0");
    const year = now.getUTCFullYear();
    const h = String(now.getUTCHours()).padStart(2, "0");
    const m = String(now.getUTCMinutes()).padStart(2, "0");
    const s = String(now.getUTCSeconds()).padStart(2, "0");
    if (clockEl) {
      clockEl.textContent = `${month} ${day}, ${year} | ${h}:${m}:${s} UTC`;
    }
  }
  setInterval(updateHeaderClock, 1000);
  updateHeaderClock();

  // 2. Initialize Leaflet Map (Centered on India matching reference image)
  const defaultCenter = [22.0, 79.5];
  const defaultZoom = 5;

  const map = L.map("map", {
    center: defaultCenter,
    zoom: defaultZoom,
    minZoom: 4,
    maxZoom: 18,
    zoomControl: false,
    attributionControl: false,
  });

  // Base Layers — ESRI Satellite Imagery + Reference Boundaries/Labels (Matches Reference Image)
  const esriSatellite = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    { maxZoom: 18 }
  ).addTo(map);

  const esriBoundaries = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
    { maxZoom: 18, opacity: 0.85 }
  ).addTo(map);

  // Alternative Basemaps
  const cartoDark = L.tileLayer(
    "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
    { maxZoom: 19 }
  );

  const osmStreet = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    { maxZoom: 19 }
  );

  let isSatellite = true;
  const layerToggleBtn = document.getElementById("toolLayerToggle");
  if (layerToggleBtn) {
    layerToggleBtn.addEventListener("click", () => {
      if (isSatellite) {
        map.removeLayer(esriSatellite);
        map.removeLayer(esriBoundaries);
        cartoDark.addTo(map);
        isSatellite = false;
        layerToggleBtn.title = "Current: Dark Matter (Click for Satellite)";
      } else {
        map.removeLayer(cartoDark);
        esriSatellite.addTo(map);
        esriBoundaries.addTo(map);
        isSatellite = true;
        layerToggleBtn.title = "Current: Satellite (Click for Dark)";
      }
    });
  }

  // Force Leaflet to compute full dimensions immediately
  setTimeout(() => {
    map.invalidateSize();
  }, 150);

  window.addEventListener("resize", () => {
    map.invalidateSize();
  });

  // Zoom & Recenter Controls
  document.getElementById("zoomInBtn")?.addEventListener("click", () => map.zoomIn());
  document.getElementById("zoomOutBtn")?.addEventListener("click", () => map.zoomOut());
  document.getElementById("toolRecenter")?.addEventListener("click", () => {
    map.flyTo(defaultCenter, defaultZoom, { duration: 1.2 });
  });

  document.getElementById("toolFullscreen")?.addEventListener("click", () => {
    const el = document.querySelector(".map-viewport-wrapper") || document.documentElement;
    if (!document.fullscreenElement) {
      el.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  });

  // Layers
  const industrialLayer = L.layerGroup().addTo(map);
  const hotspotsLayer = L.layerGroup().addTo(map);

  // 3. Load Hotspots & Industrial Polygons
  const rawClusters = window.GEOCONTEXT_DATA?.clusters || [];
  const industrialGeoJSON = window.GEOCONTEXT_DATA?.industrial_zones || null;

  // Render Industrial Polygons (Delicate dashed amber boundaries)
  if (industrialGeoJSON && industrialGeoJSON.features) {
    L.geoJSON(industrialGeoJSON, {
      style: {
        color: "#f59e0b",
        weight: 1.5,
        dashArray: "4, 4",
        fillColor: "#f59e0b",
        fillOpacity: 0.1,
      },
      onEachFeature: (feature, layer) => {
        const name = feature.properties?.name || "Industrial Belt";
        layer.bindTooltip(`<b>${name}</b><br><span style="font-size:10px;color:#cbd5e1;">Designated Industrial Zone</span>`, {
          className: "hud-tooltip-card",
          sticky: true,
        });
      },
    }).addTo(industrialLayer);
  }

  // 4. Custom Hover Tooltip DOM Element
  const tooltipBox = document.createElement("div");
  tooltipBox.className = "hud-tooltip-card";
  tooltipBox.style.position = "absolute";
  tooltipBox.style.display = "none";
  tooltipBox.style.zIndex = "2500";
  document.body.appendChild(tooltipBox);

  // 5. Incident Drawer Elements
  const drawer = document.getElementById("incidentDrawer");
  const drawerTitle = document.getElementById("drawerTitle");
  const drawerBadge = document.getElementById("drawerBadge");
  const drawerCoords = document.getElementById("drawerCoords");
  const drawerDetections = document.getElementById("drawerDetections");
  const drawerFrp = document.getElementById("drawerFrp");
  const drawerDistance = document.getElementById("drawerDistance");
  const drawerFacility = document.getElementById("drawerFacility");
  const drawerRecurrence = document.getElementById("drawerRecurrence");
  const drawerScore = document.getElementById("drawerScore");
  const drawerLabel = document.getElementById("drawerLabel");
  const drawerFocusBtn = document.getElementById("drawerFocusBtn");

  let activeMarkerIncident = null;

  document.getElementById("drawerCloseBtn")?.addEventListener("click", () => {
    drawer.classList.remove("open");
  });

  if (drawerFocusBtn) {
    drawerFocusBtn.addEventListener("click", () => {
      if (activeMarkerIncident) {
        map.flyTo([activeMarkerIncident.lat, activeMarkerIncident.lon], 12, { duration: 1 });
      }
    });
  }

  // 6. Render Hotspot Markers (Pulsing, Non-Crowded, Color-Categorized)
  const counts = { critical: 0, high: 0, moderate: 0, normal: 0 };

  rawClusters.forEach(item => {
    const tier = item.tier || "normal";
    counts[tier] = (counts[tier] || 0) + 1;

    const isCritical = tier === "critical";
    const customHtml = `
      <div class="hotspot-custom-marker ${tier}">
        <div class="marker-pulse-ring"></div>
        ${isCritical ? '<div class="marker-pulse-ring delay"></div>' : ''}
        <div class="marker-inner-dot"></div>
      </div>
    `;

    const icon = L.divIcon({
      html: customHtml,
      className: "",
      iconSize: [20, 20],
      iconAnchor: [10, 10],
    });

    const marker = L.marker([item.lat, item.lon], { icon }).addTo(hotspotsLayer);

    // Hover Interaction: HUD Tooltip
    marker.on("mouseover", (e) => {
      const tierLabel = tier.toUpperCase();
      tooltipBox.innerHTML = `
        <div class="hud-tooltip-badge ${tier}">● ${tierLabel} ANOMALY</div>
        <div class="hud-tooltip-title">${item.name || ('Cluster #' + item.id)}</div>
        <div class="hud-tooltip-grid">
          <div class="hud-tooltip-row">
            <span class="hud-tooltip-label">FRP:</span>
            <span class="hud-tooltip-val">${item.frp} MW</span>
          </div>
          <div class="hud-tooltip-row">
            <span class="hud-tooltip-label">Detections:</span>
            <span class="hud-tooltip-val">${item.detections} pts</span>
          </div>
          <div class="hud-tooltip-row">
            <span class="hud-tooltip-label">Industrial Dist:</span>
            <span class="hud-tooltip-val">${item.distance_m} m</span>
          </div>
          <div class="hud-tooltip-row">
            <span class="hud-tooltip-label">Near Facility:</span>
            <span class="hud-tooltip-val" style="max-width:110px;text-overflow:ellipsis;overflow:hidden;white-space:nowrap;">${item.facility || 'Zoned Plant'}</span>
          </div>
        </div>
      `;
      tooltipBox.style.display = "block";
      updateTooltipPosition(e.originalEvent);
    });

    marker.on("mousemove", (e) => {
      updateTooltipPosition(e.originalEvent);
    });

    marker.on("mouseout", () => {
      tooltipBox.style.display = "none";
    });

    marker.on("click", () => {
      openIncidentDrawer(item);
    });
  });

  function updateTooltipPosition(e) {
    tooltipBox.style.left = `${e.clientX + 16}px`;
    tooltipBox.style.top = `${e.clientY - 30}px`;
  }

  function openIncidentDrawer(item) {
    activeMarkerIncident = item;
    const tier = item.tier || "normal";

    drawerTitle.textContent = `${item.name || ('Cluster #' + item.id)} Details`;
    drawerBadge.textContent = `${tier.toUpperCase()} ANOMALY`;
    drawerBadge.className = `hud-tooltip-badge ${tier}`;
    drawerCoords.textContent = `${item.lat.toFixed(4)}°N, ${item.lon.toFixed(4)}°E`;
    drawerDetections.textContent = `${item.detections} records`;
    drawerFrp.textContent = `${item.frp} MW`;
    drawerDistance.textContent = `${item.distance_m} m`;
    drawerFacility.textContent = item.facility || "Industrial Facility";
    drawerRecurrence.textContent = item.recurrence ? `${item.recurrence}%` : "Baseline";
    drawerScore.textContent = `${item.ind_score || 0}/8`;
    drawerLabel.textContent = item.label ? item.label.toUpperCase() : "VERIFIED";

    drawer.classList.add("open");
  }

  // 7. Update Map Legend Counts
  document.getElementById("legendCountCritical").textContent = counts.critical;
  document.getElementById("legendCountHigh").textContent = counts.high;
  document.getElementById("legendCountModerate").textContent = counts.moderate;
  document.getElementById("legendCountNormal").textContent = counts.normal;

  // Update Bottom Metrics (Matching reference image: 12, 28, 54)
  document.getElementById("metricCriticalVal").textContent = counts.critical;
  document.getElementById("metricHighVal").textContent = counts.high;
  document.getElementById("metricTotalVal").textContent = counts.moderate;

  // 8. Populate Live Alerts Feed (matching the exact alerts from reference image)
  const alertsFeed = document.getElementById("alertsFeed");
  const alertCandidates = rawClusters
    .filter(c => c.alert_headline)
    .slice(0, 5);

  if (alertsFeed && alertCandidates.length > 0) {
    alertsFeed.innerHTML = "";

    alertCandidates.forEach(alert => {
      const itemEl = document.createElement("div");
      itemEl.className = "alert-feed-item";

      itemEl.innerHTML = `
        <div class="alert-indicator-dot ${alert.tier}"></div>
        <div class="alert-content">
          <div class="alert-title-row">
            <span class="alert-headline">${alert.alert_headline}</span>
            <span class="alert-timestamp">${alert.time_ago || "Active"}</span>
          </div>
          <div class="alert-subline">${alert.alert_sub || (alert.distance_m + 'm from Industrial Zone')}</div>
          <div class="alert-location">${alert.location_name || 'Corridor Area'}</div>
        </div>
      `;

      itemEl.addEventListener("click", () => {
        map.flyTo([alert.lat, alert.lon], 11, { duration: 1.2 });
        openIncidentDrawer(alert);
      });

      alertsFeed.appendChild(itemEl);
    });
  }

  // 9. Interactive Map Search (Hotkey Ctrl+K or typing)
  const searchInput = document.getElementById("mapSearchInput");
  if (searchInput) {
    window.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        searchInput.focus();
      }
    });

    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.trim().toLowerCase();
      if (!query) return;

      const matched = rawClusters.find(c =>
        (c.id && c.id.toString().toLowerCase().includes(query)) ||
        (c.name && c.name.toLowerCase().includes(query)) ||
        (c.location_name && c.location_name.toLowerCase().includes(query)) ||
        (c.facility && c.facility.toLowerCase().includes(query))
      );

      if (matched) {
        map.flyTo([matched.lat, matched.lon], 11);
        openIncidentDrawer(matched);
      }
    });
  }

  // 10. Fire Activity Trend Chart
  renderTrendChart();

  function renderTrendChart() {
    const svg = document.getElementById("trendSvg");
    if (!svg) return;

    const criticalPts = [12, 18, 38, 28, 34];
    const highPts = [20, 30, 48, 42, 45];
    const moderatePts = [10, 22, 29, 25, 27];
    const normalPts = [8, 14, 18, 15, 20];

    function createSmoothPath(points, height = 70, width = 300) {
      const max = 55;
      const step = width / (points.length - 1);
      const coords = points.map((p, i) => [i * step, height - (p / max) * height]);

      let d = `M ${coords[0][0]} ${coords[0][1]}`;
      for (let i = 0; i < coords.length - 1; i++) {
        const [x0, y0] = coords[i];
        const [x1, y1] = coords[i + 1];
        const mx = (x0 + x1) / 2;
        d += ` C ${mx} ${y0}, ${mx} ${y1}, ${x1} ${y1}`;
      }
      return d;
    }

    svg.innerHTML = `
      <defs>
        <linearGradient id="gradCritical" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#ef4444" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#ef4444" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <!-- Grid lines -->
      <line x1="0" y1="18" x2="300" y2="18" stroke="rgba(255,255,255,0.06)" stroke-dasharray="3,3" />
      <line x1="0" y1="46" x2="300" y2="46" stroke="rgba(255,255,255,0.06)" stroke-dasharray="3,3" />

      <!-- Curves -->
      <path d="${createSmoothPath(normalPts)}" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" />
      <path d="${createSmoothPath(moderatePts)}" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" />
      <path d="${createSmoothPath(highPts)}" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" />
      <path d="${createSmoothPath(criticalPts)}" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" />
    `;
  }
}

// Safe initialization
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initCommandCenterMap);
} else {
  initCommandCenterMap();
}