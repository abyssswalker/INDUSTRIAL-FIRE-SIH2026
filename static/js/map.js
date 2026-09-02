// ==========================================
// INITIALIZE THE MAP
// ==========================================

// Change these coordinates to your selected Area of Interest (AOI)
const map = L.map("map").setView([21.1458, 79.0882], 8);


// ==========================================
//MAP TILES
// ==========================================

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


// ==========================================
//FAKE DATA
// ==========================================

const hotspots = [
    {
        id: 1,
        latitude: 21.1458,
        longitude: 79.0882,
        location: "Nagpur Industrial Area",
        classification: "industrial",
        confidence: 0.94,
        recurrence_count: 17,
        nearest_feature: "Steel Plant",
        distance_m: 340
    },

    {
        id: 2,
        latitude: 21.1702,
        longitude: 79.0615,
        location: "Nagpur North",
        classification: "transient",
        confidence: 0.87,
        recurrence_count: 2,
        nearest_feature: "Agricultural Area",
        distance_m: 850
    },

    {
        id: 3,
        latitude: 21.1205,
        longitude: 79.1050,
        location: "Industrial Zone",
        classification: "industrial",
        confidence: 0.91,
        recurrence_count: 14,
        nearest_feature: "Factory",
        distance_m: 420
    }
];


// ==========================================
// 4. FUNCTION TO GET MARKER COLOR
// ==========================================

function getMarkerColor(classification) {

    if (classification === "industrial") {
        return "red";
    }

    if (classification === "transient") {
        return "orange";
    }

    return "gray";
}


// ==========================================
// CREATE MARKERS
// ==========================================

hotspots.forEach(function (hotspot) {

    const color = getMarkerColor(hotspot.classification);

    const marker = L.circleMarker(
        [hotspot.latitude, hotspot.longitude],
        {
            radius: 8,
            color: color,
            fillColor: color,
            fillOpacity: 0.8
        }
    ).addTo(map);


    // ==========================================
    //CLICK EVENT
    // ==========================================

    marker.on("click", function () {

        showHotspotDetails(hotspot);

    });

});
