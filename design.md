# GeoContext-AI — Landing Page Design System & Architecture Specification

> **Document Type:** Frontend UI/UX Design System & Architectural Specification  
> **Project:** GeoContext-AI (Disaster & Industrial Fire Intelligence Platform)  
> **Event:** Smart India Hackathon 2026  
> **Source Files:** [`templates/dashboard.html`](templates/dashboard.html) | [`templates/style.css`](templates/style.css) | [`templates/map.html`](templates/map.html)

---

## 1. Executive Summary & Design Philosophy

The GeoContext-AI landing page serves as the mission-control gateway preceding the primary spatial intelligence dashboard. Unlike generic AI or corporate SaaS landing interfaces, this design is anchored in **tactical incident command**, **aerospace telemetry**, and **geospatial intelligence**.

### Core Visual Principles
* **Tactical Command Atmosphere:** Deep obsidian and navy darkness evoking real-time defense or disaster response operations centers.
* **Geospatial & Satellite Authenticity:** Elements reflect actual satellite data acquisition (NASA FIRMS VIIRS 375m), metric UTM projections (`EPSG:32644`), and DBSCAN spatial clustering.
* **Controlled Luminescence:** Accents glow selectively to guide user attention without visual noise or gratuitous flashiness.
* **Information Density with Breathing Room:** Clean negative space balances dense technical telemetry on the periphery with an unambiguous central focal point.
* **Zero Dependency Overhead:** Built strictly with vanilla HTML5, CSS3, inline SVGs, and native Canvas API for instantaneous load time and 100% offline reliability.

---

## 2. Design Tokens & Color Architecture

```
                                  COLOR PALETTE
  ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
  │  Obsidian Void  │  Glass Surface  │  Satellite Cyan │  Thermal Fire   │
  │     #060911     │  #0B1220 (72%)  │     #38BDF8     │     #F97316     │
  └─────────────────┴─────────────────┴─────────────────┴─────────────────┘
  ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
  │  Alert Amber    │  Radar Emerald  │  Primary Text   │  Muted Telemetry│
  │     #F59E0B     │     #10B981     │     #F8FAFC     │     #94A3B8     │
  └─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### 2.1 Color Variables (`:root`)
| Token | Hex / Value | Usage & Psychological Intent |
| :--- | :--- | :--- |
| `--bg-primary` | `#060911` | Deep obsidian backdrop simulating space / dark monitoring rooms. |
| `--bg-secondary` | `#0b1220` | Secondary container depth and ambient fill. |
| `--card-bg` | `rgba(11, 18, 32, 0.72)` | Glassmorphic card surfaces with `backdrop-filter: blur(14px)`. |
| `--card-border` | `rgba(56, 189, 248, 0.16)` | Subtle cyan boundary defining tactical panels. |
| `--card-border-glow` | `rgba(56, 189, 248, 0.35)` | Panel hover elevation glow. |
| `--accent-cyan` | `#38bdf8` | Satellite telemetry, radar vectors, active UI highlights. |
| `--accent-cyan-glow` | `rgba(56, 189, 248, 0.40)` | High-intensity focal aura for interactive controls. |
| `--accent-fire` | `#f97316` | Active thermal radiation, high FRP markers, and fire anomalies. |
| `--accent-amber` | `#f59e0b` | Cautionary indicators, coordinate callouts, and status warnings. |
| `--accent-emerald` | `#10b981` | Real-time system health, live operational heartbeat. |
| `--accent-danger` | `#ef4444` | High-risk industrial fire alarm status. |
| `--text-primary` | `#f8fafc` | Maximum contrast crisp white typography for headings and CTA. |
| `--text-secondary` | `#94a3b8` | Readable slate gray for body descriptions and subtext. |
| `--text-muted` | `#64748b` | Dim monospace tickers, datums, and non-intrusive metadata. |

---

## 3. Typography Hierarchy

The typographic system utilizes a three-tier font stack combining modern geometry, high readability, and aerospace monospace readouts:

```
  Space Grotesk / Orbitron ───► Headings & System Branding (Futuristic & Authoritative)
  Inter                    ───► Body Copy & Descriptions   (Optimized for Screen Clarity)
  JetBrains Mono           ───► Telemetry, Datums, Tickers (Precision Engineering Readout)
```

| Element | Font Family | Size | Weight | Tracking / Letter Spacing | Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hero Title (`GeoContext-AI`)** | Space Grotesk / Display | `clamp(42px, 5.2vw, 68px)` | 800 | `-0.5px` | Mixed |
| **Hero Tagline** | Inter | `16px` | 400 | `normal` | Sentence |
| **Command Button** | Space Grotesk | `15px` | 700 | `2.2px` | Uppercase |
| **Panel Titles (H2)** | Space Grotesk | `18px` | 700 | `1.0px` | Uppercase |
| **Panel Sub-Headings** | Inter | `12px` | 600 | `normal` | Title Case |
| **Panel Body Text** | Inter | `11px - 13px` | 400 | `normal` | Sentence |
| **Telemetry & Status Bar** | JetBrains Mono | `10px - 11px` | 500-700 | `1.0px - 2.0px` | Uppercase |

---

## 4. Atmospheric Visual Architecture

The background is composed of multiple independent GPU-composited layers that simulate an active geospatial radar scope:

```
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. Deep Space Obsidian Base Layer (#060911)                 │
  ├─────────────────────────────────────────────────────────────┤
  │ 2. Telemetry Canvas (Grid, Rotating Sweep, Floating Embers) │
  ├─────────────────────────────────────────────────────────────┤
  │ 3. Ambient Radial Vignette (Edge Falloff & Depth)           │
  ├─────────────────────────────────────────────────────────────┤
  │ 4. Optical Scanline Texture Overlay (CRT / Tactical HUD)   │
  ├─────────────────────────────────────────────────────────────┤
  │ 5. Glassmorphic UI Layer (Header, Hero, Panels, Footer)     │
  └─────────────────────────────────────────────────────────────┘
```

### 4.1 HTML5 Dynamic Telemetry Canvas (`#telemetry-canvas`)
- **Coordinate Grid:** Renders an 80px metric grid with ultra-subtle cyan lines (`rgba(56, 189, 248, 0.035)`) representing map graticules.
- **Concentric Radar Sweep:** Three concentric radar range rings (160px, 260px, 380px) centered dynamically behind the Hero section with a continuous 360° rotating radar sweep line (`0.007 rad/frame`).
- **Thermal & Telemetry Particles:** 45 active particles floating upward:
  - 65% Cyan Telemetry Nodes (`rgba(56, 189, 248, α)`): Represent satellite observations and data packets.
  - 35% Orange Thermal Embers (`rgba(249, 115, 22, α)`): Represent Fire Radiative Power (FRP) detection signals.
- **Parallax Physics:** Mouse position subtly shifts the radar center (`dx * 0.02, dy * 0.02`), adding an illusion of three-dimensional HUD perspective.

### 4.2 Optical Scanline & Vignette
- `.ambient-vignette`: Multi-stop radial gradient darkening the edges to focus human gaze onto the central call-to-action.
- `.scanline-overlay`: 4px repeating micro-raster scanlines (`opacity: 0.65`) providing tactical display texture without degrading text sharpness.

---

## 5. Layout & Information Architecture

The interface uses a full-viewport responsive layout (`min-height: 100vh`) organized into three main regions:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ [TOP HUD]  GEOCONTEXT-AI // v1.0.4    ● SYSTEM ACTIVE   SENSOR: VIIRS   UTC  │
├──────────────────────────────────────────────────────────────────────────────┤
│                │                                            │                │
│  [LEFT PANEL]  │               [CENTER HERO]                │ [BOTTOM-RIGHT] │
│                │                                            │                │
│  What is       │               GeoContext-AI                │   BUILT BY     │
│  GeoContext-AI │                                            │   GeoContext   │
│                │   "Autonomous satellite thermal anomaly    │   Team         │
│  4 Analytical  │    detection, spatial clustering..."       │                │
│  Pillars:      │                                            │   SIH 2026     │
│  - FIRMS VIIRS │      ┌─────────────────────────────┐       │   Smart India  │
│  - DBSCAN      │      │    ENTER COMMAND CENTER     │       │   Hackathon    │
│  - OSM/Bhuvan  │      └─────────────────────────────┘       │                │
│  - FRP Scoring │                                            │                │
│                │      PILOT: CHHATTISGARH CORRIDOR          │                │
│                │                                            │                │
├──────────────────────────────────────────────────────────────────────────────┤
│ [BOTTOM HUD]  DATUM: WGS-84/UTM-44N   RES: 375m   ALGO: DBSCAN (eps=500m)   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Top HUD Header
- **Identity:** Tactical radar icon + `GEOCONTEXT-AI` + `Incident Command & Satellite Analytics`.
- **System Indicator:** Glowing emerald pulsating dot (`@keyframes pulse-emerald`) showing real-time operational status.
- **Sensor Specification:** Real NASA sensor designation (`VIIRS NOAA-20 NRT`).
- **Live Clock:** Native JavaScript interval generating live formatted UTC telemetry (`UTC HH:MM:SS`).

### 5.2 Left Panel: "WHAT IS GEOCONTEXT-AI?"
A structured glass card presenting the actual, un-fabricated architecture of the data pipeline:
1. **Satellite Thermal Telemetry:** NASA FIRMS VIIRS 375m active fire data + Fire Radiative Power (FRP).
2. **Metric Spatial Clustering:** UTM Zone 44N (`EPSG:32644`) DBSCAN density clustering to isolate distinct fire clusters and centroids.
3. **Industrial Spatial Context:** Haversine distance matching and 5km density metrics against OpenStreetMap & Bhuvan industrial zones.
4. **Multi-Signal Classification:** Scoring based on recurrence rates, FRP variance coefficients (`frp_cv`), day/night ratios, and cluster baseline Z-scores.

### 5.3 Center Hero: Primary Focal Point
- **Status Eyebrow:** `● REAL-TIME INCIDENT COMMAND INTELLIGENCE` with animated amber border breathing.
- **Main Heading:** `GeoContext-AI` styled with a metallic-to-cyan gradient (`linear-gradient(135deg, #fff, #bae6fd, #38bdf8)`) and high-radius ambient drop-shadow.
- **Tagline:** Precise statement of capability without generic buzzwords.
- **Primary Action Button:**
  - Label: `ENTER COMMAND CENTER`
  - High-visibility tactical gradient (`#0284c7` to `#0c4a6e`) with animated specular light sweep on hover (`::before` reflection).
  - Tactical directional chevron SVG that translates rightward on hover.
  - Linked to existing dashboard file: `map.html`.
- **Pilot Readout:** `PILOT ZONE: CHHATTISGARH CORRIDOR [21.5°N, 82.0°E]`.

### 5.4 Bottom-Right Panel: Team & Event Attribution
- Subtle glassmorphic card anchored to the lower-right quadrant.
- **Built By:** `GeoContext-AI Team`.
- **Badge:** `SIH 2026` badge in amber/fire glow.
- **Context:** `Smart India Hackathon` — `Disaster & Industrial Hazard AI`.

### 5.5 Bottom HUD Telemetry Footer
- Minimal horizontal status bar detailing projection datum (`WGS-84 / UTM-44N`), spatial resolution (`375m SATELLITE I-BAND`), and algorithmic parameters (`DBSCAN eps=500m`).

---

## 6. Interaction Design & Transitions

### 6.1 Interactive Micro-States
| Element | State | Effect |
| :--- | :--- | :--- |
| **`btn-command-center`** | Default | Deep blue gradient, cyan border (`rgba(56,189,248,0.6)`), outer cyan glow. |
| | Hover | `transform: translateY(-2px) scale(1.02)`, specular sweep slides across, glow expands to 45px. |
| | Active | `transform: translateY(1px) scale(0.99)`. |
| **`capability-item`** | Hover | `transform: translateX(3px)`, border illuminates cyan, subtle background shift. |
| **`team-card`** | Hover | `transform: translateY(-2px)`, top amber accent line intensifies. |

### 6.2 Tactical Shutter Transition (`#launchShutter`)
When **ENTER COMMAND CENTER** is clicked:
1. The button label updates to `"LAUNCHING..."`.
2. A high-priority tactical shutter overlay (`#launchShutter`) fades in with a high-speed orbital spinner and status text: `"INITIALIZING COMMAND CENTER HUD..."`.
3. After a 360ms cinematic delay, the browser navigates smoothly to `map.html`.
4. *Graceful degradation:* If JavaScript is disabled or users middle-click / Ctrl-click, native HTML `<a href="map.html">` navigates immediately without interruption.

---

## 7. Responsive Breakpoint Matrix

| Viewport | Target Device | Layout Adjustments |
| :--- | :--- | :--- |
| **> 1280px** | 1080p Desktop / Projector | Full 3-column asymmetric layout (`380px 1fr 320px`), generous negative space. |
| **1024px – 1280px** | 1366×768 Laptops / Screens | Scaled columns (`340px 1fr 280px`), adjusted hero title to 52px. |
| **768px – 1023px** | Tablets / Small Laptops | Grid switches to stacked 1-column layout: Center Hero moves to top (`order: 1`), followed by Left Panel (`order: 2`), then Team Card (`order: 3`). |
| **< 768px** | Mobile Viewports | Top HUD collapses to vertical stack; Hero title scales to 38px; radar ring scales down to 320px; footer elements stack. |

---

## 8. Performance & Code Quality Benchmarks

- **Zero Framework Footprint:** No React, Vue, Bootstrap JS, or Tailwind compile steps required.
- **Zero Third-Party Icon Fonts:** All icons are lightweight, inline, resolution-independent SVGs that render instantly with zero network requests.
- **60 FPS Rendering:** Canvas draws only mathematical primitives and lightweight particle arrays using `requestAnimationFrame` with zero memory leaks.
- **Self-Contained Portability:** Works equally well opened directly in a browser via `file://` or hosted on an asynchronous production server (FastAPI, Nginx, Docker).
