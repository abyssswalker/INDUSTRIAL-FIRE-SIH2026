const CHHATTISGARH_CENTER = [21.2787, 81.8661];
const INITIAL_ZOOM = 7;

const CLASSIFICATION_COLORS = {
    industrial: "#dc2626",
    wildfire: "#f97316",
    uncertain: "#ca8a04",
};

const CLASSIFICATION_LABELS = {
    industrial: "Industrial",
    wildfire: "Wildfire",
    uncertain: "Uncertain",
};

let map;
let markerLayer;
let allHotspots = [];
let visibleHotspots = [];

document.addEventListener("DOMContentLoaded", async () => {
    initializeMap();
    initializeControls();
    await loadHotspots();
});

function initializeMap() {
    map = L.map("map", {
        zoomControl: true,
        preferCanvas: true,
    }).setView(CHHATTISGARH_CENTER, INITIAL_ZOOM);

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
    }).addTo(map);

    markerLayer = L.layerGroup().addTo(map);
}

function initializeControls() {
    document.getElementById("classificationFilter").addEventListener("change", applyFilters);
    document.getElementById("searchInput").addEventListener("input", applyFilters);
    document.getElementById("resetButton").addEventListener("click", resetFilters);
}

async function loadHotspots() {
    try {
        const response = await fetch("/hotspots");
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        allHotspots = Array.isArray(data) ? data : [];
        visibleHotspots = [...allHotspots];

        updateDashboard(visibleHotspots);
        renderMarkers(visibleHotspots);
        showLiveStatus();

        if (visibleHotspots.length > 0) {
            map.fitBounds(
                visibleHotspots.map((hotspot) => [hotspot.centroid_lat, hotspot.centroid_lon]),
                {
                    padding: [35, 35],
                    maxZoom: 8,
                }
            );
        }
    } catch (error) {
        console.error("Failed to load hotspots:", error);
        showDemoOrErrorStatus();
    }
}

function applyFilters() {
    const classification = document.getElementById("classificationFilter").value;
    const searchTerm = document.getElementById("searchInput").value.trim().toLowerCase();

    visibleHotspots = allHotspots.filter((hotspot) => {
        const classificationMatches =
            classification === "all" || hotspot.classification === classification;

        const searchableText = [
            hotspot.classification,
            hotspot.nearest_industrial_name,
            hotspot.nearest_industrial_type,
            hotspot.nearest_osm_id,
            String(hotspot.cluster_id),
        ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

        const searchMatches = !searchTerm || searchableText.includes(searchTerm);
        return classificationMatches && searchMatches;
    });

    updateDashboard(visibleHotspots);
    renderMarkers(visibleHotspots);
}

function resetFilters() {
    document.getElementById("classificationFilter").value = "all";
    document.getElementById("searchInput").value = "";
    visibleHotspots = [...allHotspots];

    updateDashboard(visibleHotspots);
    renderMarkers(visibleHotspots);

    if (visibleHotspots.length > 0) {
        map.fitBounds(
            visibleHotspots.map((hotspot) => [hotspot.centroid_lat, hotspot.centroid_lon]),
            {
                padding: [35, 35],
                maxZoom: 8,
            }
        );
    }
}

function renderMarkers(hotspots) {
    markerLayer.clearLayers();

    hotspots.forEach((hotspot) => {
        createHotspotMarker(hotspot).addTo(markerLayer);
    });

    document.getElementById("resultCount").textContent =
        `${hotspots.length} hotspot${hotspots.length === 1 ? "" : "s"} shown`;
}

function createHotspotMarker(hotspot) {
    const color = CLASSIFICATION_COLORS[hotspot.classification] || CLASSIFICATION_COLORS.uncertain;

    const marker = L.circleMarker([hotspot.centroid_lat, hotspot.centroid_lon], {
        radius: getMarkerRadius(hotspot),
        color: "#ffffff",
        weight: 2,
        fillColor: color,
        fillOpacity: 0.9,
    });

    marker.bindPopup(createPopupContent(hotspot), { maxWidth: 280 });

    marker.on("click", () => {
        showHotspotDetails(hotspot);
    });

    return marker;
}

function getMarkerRadius(hotspot) {
    const count = Number(hotspot.detection_count) || 1;
    return Math.min(15, Math.max(7, 6 + Math.sqrt(count)));
}

function createPopupContent(hotspot) {
    const label = CLASSIFICATION_LABELS[hotspot.classification] || "Uncertain";
    const color = CLASSIFICATION_COLORS[hotspot.classification] || CLASSIFICATION_COLORS.uncertain;

    return `
        <div class="popup-title">Cluster #${escapeHtml(hotspot.cluster_id)}</div>
        <div class="popup-classification" style="color: ${color}">${escapeHtml(label)}</div>
        <div class="popup-row">Detections: ${formatNumber(hotspot.detection_count)}</div>
        <div class="popup-row">FRP mean: ${formatNumber(hotspot.frp_mean)} MW</div>
        <div class="popup-row">Last seen: ${formatDate(hotspot.last_seen)}</div>
    `;
}

function showHotspotDetails(hotspot) {
    const detailPanel = document.getElementById("detailPanel");
    const classification = hotspot.classification || "uncertain";
    const label = CLASSIFICATION_LABELS[classification] || "Uncertain";

    const modelConfidence =
        hotspot.confidence === null || hotspot.confidence === undefined
            ? "Not available"
            : `${(Number(hotspot.confidence) * 100).toFixed(1)}%`;

    const osmName = hotspot.nearest_industrial_name || "No joined OSM name";
    const osmType = hotspot.nearest_industrial_type || "Not available";

    const distance =
        hotspot.nearest_industrial_distance_m === null || hotspot.nearest_industrial_distance_m === undefined
            ? "Not available"
            : `${formatNumber(hotspot.nearest_industrial_distance_m)} m`;

    detailPanel.innerHTML = `
        <div class="detail-content">
            <div class="detail-header">
                <div>
                    <h2>Cluster #${escapeHtml(hotspot.cluster_id)}</h2>
                    <p>Last seen ${formatDate(hotspot.last_seen)}</p>
                </div>
                <span class="classification-badge badge-${classification}">${escapeHtml(label)}</span>
            </div>

            <div class="detail-section">
                <h3>Classification</h3>
                ${detailRow("Label", label)}
                ${detailRow("Model confidence", modelConfidence)}
                ${detailRow("Classifier version", hotspot.classifier_version || "Not available")}
            </div>

            <div class="detail-section">
                <h3>Location</h3>
                ${detailRow("Latitude", formatNumber(hotspot.centroid_lat))}
                ${detailRow("Longitude", formatNumber(hotspot.centroid_lon))}
                ${detailRow("OSM ID", hotspot.nearest_osm_id || "Not available")}
                ${detailRow("OSM name", osmName)}
                ${detailRow("OSM type", osmType)}
                ${detailRow("Distance to industrial site", distance)}
            </div>

            <div class="detail-section">
                <h3>Detection statistics</h3>
                ${detailRow("Detection count", formatNumber(hotspot.detection_count))}
                ${detailRow("First seen", formatDate(hotspot.first_seen))}
                ${detailRow("Last seen", formatDate(hotspot.last_seen))}
                ${detailRow("Months active", formatNumber(hotspot.months_active))}
                ${detailRow("Recurrence rate", formatNumber(hotspot.recurrence_rate))}
            </div>

            <div class="detail-section">
                <h3>Fire measurements</h3>
                ${detailRow("FRP mean", `${formatNumber(hotspot.frp_mean)} MW`)}
                ${detailRow("FRP standard deviation", `${formatNumber(hotspot.frp_std)} MW`)}
                ${detailRow("FRP coefficient of variation", formatNumber(hotspot.frp_cv))}
                ${detailRow("Day detections", formatNumber(hotspot.day_count))}
                ${detailRow("Night detections", formatNumber(hotspot.night_count))}
                ${detailRow("Day/night ratio", formatNumber(hotspot.daynight_ratio))}
            </div>
        </div>
    `;

    if (window.innerWidth < 1200) {
        detailPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    }
}

function detailRow(label, value) {
    return `
        <div class="detail-row">
            <span>${escapeHtml(label)}</span>
            <span>${escapeHtml(value)}</span>
        </div>
    `;
}

function updateDashboard(hotspots) {
    const industrial = hotspots.filter((h) => h.classification === "industrial").length;
    const wildfire = hotspots.filter((h) => h.classification === "wildfire").length;
    const uncertain = hotspots.filter((h) => h.classification === "uncertain").length;

    document.getElementById("totalCount").textContent = hotspots.length;
    document.getElementById("industrialCount").textContent = industrial;
    document.getElementById("wildfireCount").textContent = wildfire;
    document.getElementById("uncertainCount").textContent = uncertain;
}

function showLiveStatus() {
    document.getElementById("connectionDot").style.background = "#22c55e";
    document.getElementById("connectionText").textContent = "Live database connected";
}

function showDemoOrErrorStatus() {
    document.getElementById("connectionDot").style.background = "#ef4444";
    document.getElementById("connectionText").textContent = "API unavailable";
}

function formatNumber(value) {
    if (value === null || value === undefined || value === "") return "Not available";
    const number = Number(value);
    if (Number.isNaN(number)) return "Not available";
    return number.toLocaleString("en-IN", { maximumFractionDigits: 4 });
}

function formatDate(value) {
    if (!value) return "Not available";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "Not available";
    return date.toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}

function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}