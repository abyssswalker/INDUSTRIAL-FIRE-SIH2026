import json

# Read CSS
with open('static/css/map-dashboard.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

# Read Dataset
with open('static/js/dataset.js', 'r', encoding='utf-8') as f:
    dataset_content = f.read()

# Read Map JS Logic
with open('static/js/map.js', 'r', encoding='utf-8') as f:
    map_js_content = f.read()

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>GeoContext-AI — Incident Command Center</title>

  <!-- Typography: Inter, Space Grotesk, JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700;800&display=swap"
    rel="stylesheet"
  />

  <!-- Leaflet Map CSS -->
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    crossorigin=""
  />

  <!-- Fully Embedded Self-Contained Stylesheet -->
  <style>
{css_content}
  </style>
</head>
<body>

  <div class="dashboard-root">

    <!-- Top Header Bar -->
    <header class="top-header">
      <div class="brand-section">
        <div class="brand-logo-icon">
          <!-- Globe Grid Vector Icon with explicit dimensions -->
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="2" y1="12" x2="22" y2="12"></line>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
          </svg>
        </div>
        <div class="brand-titles">
          <a href="dashboard.html" class="brand-title">GeoContext<span class="highlight">-AI</span></a>
          <span class="brand-tagline">Geospatial Intelligence for a Safer Tomorrow</span>
        </div>
      </div>

      <div class="header-status-section">
        <div class="system-status-badge">
          <span class="pulse-dot"></span>
          <span>System Online</span>
        </div>
        <div id="headerClock" class="header-clock">Apr 12, 2026 | 14:32 UTC</div>
        <div class="header-actions">
          <button class="icon-btn" title="Toggle Display Mode" aria-label="Toggle Display Mode">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
          </button>
          <div class="avatar-badge" title="Incident Commander">GC</div>
        </div>
      </div>
    </header>

    <!-- Dashboard Body: Sidebar + Main Content -->
    <div class="dashboard-body">

      <!-- Left Navigation Sidebar -->
      <aside class="left-sidebar">
        <nav class="nav-group">
          <a href="dashboard.html" class="nav-link-item">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            <span class="nav-label">Home</span>
          </a>
          <a href="#" class="nav-link-item active">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
              <line x1="8" y1="2" x2="8" y2="18"></line>
              <line x1="16" y1="6" x2="16" y2="22"></line>
            </svg>
            <span class="nav-label">Live Map</span>
          </a>
          <a href="#alertsFeed" class="nav-link-item">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            <span class="nav-label">Alerts</span>
            <span class="nav-badge">12</span>
          </a>
          <a href="#insightsCard" class="nav-link-item">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
            <span class="nav-label">Analytics</span>
          </a>
          <a href="#dataSourcesCard" class="nav-link-item">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <span class="nav-label">Reports</span>
          </a>
          <a href="#" class="nav-link-item">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
            <span class="nav-label">Settings</span>
          </a>
        </nav>

        <div class="sidebar-bottom-card">
          <div class="sidebar-brand-text">
            Smarter<br />Data.<br />Safer<br />Communities.
          </div>
          <div class="sidebar-brand-accent"></div>
          <!-- Mountain Vector Silhouette with fixed height -->
          <svg class="mountain-bg-art" width="100%" height="48" viewBox="0 0 200 60" preserveAspectRatio="none">
            <polygon points="0,60 30,35 65,50 110,20 150,45 200,10 200,60" fill="#38bdf8"></polygon>
          </svg>
        </div>
      </aside>

      <!-- Center Stage Area -->
      <main class="center-stage">

        <!-- Upper Workspace: Map (The Hero) + Right Stack -->
        <div class="upper-workspace">

          <!-- The Map Viewport (Hero Element) -->
          <div class="map-viewport-wrapper">
            <!-- Floating Search Input -->
            <div class="map-search-bar">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <input
                id="mapSearchInput"
                type="text"
                class="map-search-input"
                placeholder="Search location, industry, or coordinates..."
              />
              <span class="search-shortcut-badge">Ctrl K</span>
            </div>

            <!-- Floating Action Tools (Top-Right) -->
            <div class="map-floating-tools">
              <button id="toolLayerToggle" class="tool-action-btn" title="Toggle Basemap (Satellite / Dark)">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                  <polyline points="2 17 12 22 22 17"></polyline>
                  <polyline points="2 12 12 17 22 12"></polyline>
                </svg>
              </button>
              <button id="toolRecenter" class="tool-action-btn" title="Recenter on India Subcontinent">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="3 11 22 2 13 21 11 13 3 11"></polygon>
                </svg>
              </button>
              <button class="tool-action-btn" title="3D Terrain Mode (Perspective)">3D</button>
              <button id="toolFullscreen" class="tool-action-btn" title="Fullscreen Viewport">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
                </svg>
              </button>
            </div>

            <!-- Floating Zoom Controls -->
            <div class="map-zoom-tools">
              <button id="zoomInBtn" class="tool-action-btn" title="Zoom In">+</button>
              <button id="zoomOutBtn" class="tool-action-btn" title="Zoom Out">−</button>
            </div>

            <!-- Floating Legend (Bottom-Left) -->
            <div class="map-legend-card">
              <div class="legend-item">
                <div class="legend-label-group">
                  <span class="legend-dot critical"></span>
                  <span>Critical Fire</span>
                </div>
                <span id="legendCountCritical" class="legend-count">12</span>
              </div>
              <div class="legend-item">
                <div class="legend-label-group">
                  <span class="legend-dot high"></span>
                  <span>High Risk</span>
                </div>
                <span id="legendCountHigh" class="legend-count">28</span>
              </div>
              <div class="legend-item">
                <div class="legend-label-group">
                  <span class="legend-dot moderate"></span>
                  <span>Moderate</span>
                </div>
                <span id="legendCountModerate" class="legend-count">54</span>
              </div>
              <div class="legend-item">
                <div class="legend-label-group">
                  <span class="legend-dot normal"></span>
                  <span>Normal</span>
                </div>
                <span id="legendCountNormal" class="legend-count">93</span>
              </div>
              <div class="legend-divider"></div>
              <div class="legend-industrial-row">
                <span class="legend-industrial-icon"></span>
                <span>Industrial Zone</span>
              </div>
            </div>

            <!-- Floating Scale Bar (Bottom-Right) -->
            <div class="map-scale-readout">
              <div class="scale-ticks">
                <span>0</span>
                <span>250</span>
                <span>500</span>
                <span>1,000 km</span>
              </div>
              <div class="scale-ruler"></div>
            </div>

            <!-- Leaflet Container -->
            <div id="map"></div>
          </div>

          <!-- Right-Side Stack: Live Alerts + Fire Activity Trend -->
          <div class="right-stack">

            <!-- Live Alerts Panel -->
            <div class="dashboard-card live-alerts-card">
              <div class="card-header-row">
                <div class="card-title-group">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                  </svg>
                  <span>Live Alerts</span>
                </div>
                <a href="#alertsFeed" class="card-sublink">View All →</a>
              </div>

              <div id="alertsFeed" class="alerts-feed-scroll">
                <!-- Dynamically populated by JS from dataset -->
                <div class="alert-feed-item">
                  <div class="alert-indicator-dot critical"></div>
                  <div class="alert-content">
                    <div class="alert-title-row">
                      <span class="alert-headline">Critical Fire Detected</span>
                      <span class="alert-timestamp">12m ago</span>
                    </div>
                    <div class="alert-subline">2.4 km from Industrial Zone</div>
                    <div class="alert-location">Nagpur, Maharashtra</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Fire Activity Trend Chart -->
            <div class="dashboard-card trend-card">
              <div class="card-header-row" style="margin-bottom: 4px;">
                <div class="card-title-group">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                  </svg>
                  <span>Fire Activity Trend</span>
                </div>
                <span style="font-size: 10px; color: var(--text-dim);">Last 24 Hours</span>
              </div>

              <!-- SVG Smooth Line Curves -->
              <svg id="trendSvg" class="chart-svg-container" viewBox="0 0 300 75" preserveAspectRatio="none"></svg>

              <div class="chart-timeline-labels">
                <span>00:00</span>
                <span>06:00</span>
                <span>12:00</span>
                <span>18:00</span>
                <span>24:00</span>
              </div>

              <div class="chart-legend-row">
                <div class="chart-legend-pill"><span class="legend-dot critical" style="width:6px;height:6px;"></span> Critical</div>
                <div class="chart-legend-pill"><span class="legend-dot high" style="width:6px;height:6px;"></span> High</div>
                <div class="chart-legend-pill"><span class="legend-dot moderate" style="width:6px;height:6px;"></span> Moderate</div>
                <div class="chart-legend-pill"><span class="legend-dot normal" style="width:6px;height:6px;"></span> Normal</div>
              </div>
            </div>

          </div>

        </div>

        <!-- Lower Workspace: 4 Cards Below Map -->
        <div class="lower-workspace">

          <!-- Card 1: Our Mission -->
          <div class="dashboard-card mission-card">
            <div class="mission-card-bg"></div>
            <div class="mission-content">
              <span class="mission-eyebrow">OUR MISSION</span>
              <h3 class="mission-title">Protecting Industries. Preserving Lives.</h3>
              <p class="mission-desc">
                GeoContext-AI correlates satellite thermal observations, spatial context, and statistical scoring to isolate anomalous industrial fires.
              </p>
              <a href="dashboard.html" class="mission-btn">
                <span>Learn More</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </a>
            </div>
          </div>

          <!-- Card 2: Key Insights Metrics -->
          <div id="insightsCard" class="dashboard-card insights-card">
            <div class="card-header-row">
              <div class="card-title-group">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="9" y1="3" x2="9" y2="21"></line>
                </svg>
                <span>Key Insights</span>
              </div>
            </div>

            <div class="metrics-row">
              <div class="metric-box">
                <div class="metric-header">
                  <div class="metric-icon-bubble critical">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2c1.5 3 4 5 4 9 0 3.3-2.7 6-6 6s-6-2.7-6-6c0-4 2.5-6 4-9 1 2 2 3 4 0z"></path>
                    </svg>
                  </div>
                  <span class="metric-label">Critical Alerts</span>
                </div>
                <div id="metricCriticalVal" class="metric-value">12</div>
                <div class="metric-delta">↑ 2.3% from yesterday</div>
              </div>

              <div class="metric-box">
                <div class="metric-header">
                  <div class="metric-icon-bubble high">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                      <line x1="12" y1="9" x2="12" y2="13"></line>
                      <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                  </div>
                  <span class="metric-label">High Risk Zones</span>
                </div>
                <div id="metricHighVal" class="metric-value">28</div>
                <div class="metric-delta">↑ 1.1% from yesterday</div>
              </div>

              <div class="metric-box">
                <div class="metric-header">
                  <div class="metric-icon-bubble total">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
                    </svg>
                  </div>
                  <span class="metric-label">Total Hotspots</span>
                </div>
                <div id="metricTotalVal" class="metric-value">54</div>
                <div class="metric-delta">↑ 3.2% from yesterday</div>
              </div>
            </div>
          </div>

          <!-- Card 3: Data Sources -->
          <div id="dataSourcesCard" class="dashboard-card datasources-card">
            <div class="card-header-row">
              <div class="card-title-group">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                  <polyline points="2 17 12 22 22 17"></polyline>
                  <polyline points="2 12 12 17 22 12"></polyline>
                </svg>
                <span>Data Sources</span>
              </div>
            </div>

            <div class="sources-list">
              <div class="source-row">
                <div class="source-info">
                  <div class="source-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                    </svg>
                  </div>
                  <div class="source-titles">
                    <span class="source-name">NASA FIRMS</span>
                    <span class="source-role">Fire Information (VIIRS 375m)</span>
                  </div>
                </div>
                <span class="source-status-light"></span>
              </div>

              <div class="source-row">
                <div class="source-info">
                  <div class="source-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
                    </svg>
                  </div>
                  <div class="source-titles">
                    <span class="source-name">OpenStreetMap</span>
                    <span class="source-role">Industrial Spatial Polygons</span>
                  </div>
                </div>
                <span class="source-status-light"></span>
              </div>

              <div class="source-row">
                <div class="source-info">
                  <div class="source-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M12 2a10 10 0 0 0-10 10c0 4.4 2.9 8.2 7 9.5.5.1.7-.2.7-.5v-1.8c-2.8.6-3.4-1.4-3.4-1.4-.5-1.1-1.1-1.4-1.1-1.4-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.3 1.1 2.9.8.1-.6.3-1.1.6-1.4-2.2-.2-4.6-1.1-4.6-4.9 0-1.1.4-2 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.8 1a9.6 9.6 0 0 1 5 0c2-1.3 2.8-1 2.8-1 .5 1.4.2 2.4.1 2.7.6.7 1 1.6 1 2.7 0 3.8-2.4 4.7-4.6 4.9.4.3.7.9.7 1.9V21c0 .3.2.6.7.5 4.1-1.3 7-5.1 7-9.5A10 10 0 0 0 12 2z"></path>
                    </svg>
                  </div>
                  <div class="source-titles">
                    <span class="source-name">Machine Learning</span>
                    <span class="source-role">DBSCAN + Recurrence Scoring</span>
                  </div>
                </div>
                <span class="source-status-light"></span>
              </div>
            </div>
          </div>

          <!-- Card 4: Built By Team Card -->
          <div class="dashboard-card team-card">
            <div class="team-header-area">
              <span class="team-eyebrow">BUILT BY</span>
              <h4 class="team-title">GeoContext-AI Team</h4>
              <span class="team-event">Smart India Hackathon 2026</span>
            </div>

            <div class="team-wave-footer">
              <span class="team-quote">Real data. Real impact.</span>
              <!-- Topographic Wave Curve SVG with explicit dimensions -->
              <svg class="topographic-wave-svg" width="100%" height="34" viewBox="0 0 200 40" preserveAspectRatio="none">
                <path d="M0,25 Q40,5 90,28 T180,15 T200,30" fill="none" stroke="#38bdf8" stroke-width="1.2"></path>
                <path d="M0,32 Q50,15 100,35 T190,20 T200,38" fill="none" stroke="#60a5fa" stroke-width="1"></path>
                <path d="M0,38 Q60,20 120,38 T200,28" fill="none" stroke="#93c5fd" stroke-width="0.8"></path>
              </svg>
            </div>
          </div>

        </div>

      </main>

    </div>

    <!-- Slide-in Incident Detail Drawer -->
    <div id="incidentDrawer" class="incident-drawer">
      <div class="drawer-header">
        <div>
          <div id="drawerBadge" class="hud-tooltip-badge critical">CRITICAL ANOMALY</div>
          <h3 id="drawerTitle" class="drawer-title">Cluster Details</h3>
        </div>
        <button id="drawerCloseBtn" class="drawer-close-btn" title="Close Panel">✕</button>
      </div>

      <div class="drawer-body">
        <div class="drawer-stat-grid">
          <div class="drawer-stat-card">
            <span class="drawer-stat-lbl">Centroid Coordinates</span>
            <span id="drawerCoords" class="drawer-stat-val">21.37°N, 81.67°E</span>
          </div>
          <div class="drawer-stat-card">
            <span class="drawer-stat-lbl">Total Detections</span>
            <span id="drawerDetections" class="drawer-stat-val">323</span>
          </div>
          <div class="drawer-stat-card">
            <span class="drawer-stat-lbl">Mean FRP</span>
            <span id="drawerFrp" class="drawer-stat-val">2.89 MW</span>
          </div>
          <div class="drawer-stat-card">
            <span class="drawer-stat-lbl">Industrial Proximity</span>
            <span id="drawerDistance" class="drawer-stat-val">99 m</span>
          </div>
          <div class="drawer-stat-card">
            <span class="drawer-stat-lbl">Nearest Facility</span>
            <span id="drawerFacility" class="drawer-stat-val">Steel Plant</span>
          </div>
          <div class="drawer-stat-card">
            <span class="drawer-stat-lbl">Recurrence Rate</span>
            <span id="drawerRecurrence" class="drawer-stat-val">27.4%</span>
          </div>
          <div class="drawer-stat-card">
            <span class="drawer-stat-lbl">Industrial Score</span>
            <span id="drawerScore" class="drawer-stat-val">6 / 8</span>
          </div>
          <div class="drawer-stat-card">
            <span class="drawer-stat-lbl">Model Classification</span>
            <span id="drawerLabel" class="drawer-stat-val">INDUSTRIAL</span>
          </div>
        </div>

        <div class="drawer-actions">
          <button id="drawerFocusBtn" class="drawer-btn primary">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="22" y1="12" x2="18" y2="12"></line>
              <line x1="6" y1="12" x2="2" y2="12"></line>
              <line x1="12" y1="6" x2="12" y2="2"></line>
              <line x1="12" y1="22" x2="12" y2="18"></line>
            </svg>
            <span>Focus on Map</span>
          </button>
        </div>
      </div>
    </div>

  </div>

  <!-- Leaflet Map JS Library -->
  <script
    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
    crossorigin=""
  ></script>

  <!-- Embedded Authentic Dataset -->
  <script>
{dataset_content}
  </script>

  <!-- Embedded Controller Logic -->
  <script>
{map_js_content}
  </script>

</body>
</html>
"""

with open('templates/map.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print('Successfully created fully self-contained templates/map.html! Size:', len(html_template), 'bytes')
