# Integrated-Land-And-Air-Optimized-Routing
# 🚗✈️ Land and Air Routing Optimization System

This project features two distinct yet complementary modules for optimizing transportation routes within India: one for **land-based routing** and another for **air-based flight routing**. Each module leverages real-time APIs and powerful data processing libraries to deliver accurate, efficient route planning.

---

## 📦 Modules Overview

### 1. Land Routing Module (`land.py`)

#### 🧠 System Design
- **Type**: GUI-based desktop application using **StreamLit**
- **Architecture**: Three-tier client-server model
  - **Presentation Layer**: GUI for input/output
  - **Logic Layer**: Dijkstra-based route calculation with traffic simulation (Manually)
  - **Data Layer**: OpenRouteService API for Mapinformation, Graph and geocoding

#### ⚙️ Key Components
- **Geocoding**: `geopy.Nominatim` for address-to-coordinates conversion
- **Routing Engine**: 
  - OpenRouteService API for distance, duration, and route geometry
  - Multiple alternate routes
- **Mapping**: `folium` for interactive map visualization with traffic indicators
- **Traffic Visualization**: Google Maps-style traffic segments (green/orange/red)

---

### 2. Air Routing Module (`air_routing.py`)

#### 🧠 System Design
- **Type**: Command-line application for testing and Streamlit for GUI
- **Architecture**: Batch processing system with real-time API integration

#### ⚙️ Core Features
- **Real-time Flight Data**: Uses AviationStack API to fetch live flight data
- **Routing Logic**:
  - Direct flight finder (point-to-point)
  - Two-stage connection analysis with smart layover handling
- **Data Processing**: `pandas` for tabular data manipulation and filtering
- **Connection Rules**:
  - Layover duration filtering (1–2 hours)
  - Valid airport transitions only
- **Output**: Clean, human-readable flight tables in the CLI

---

## 🧰 Installation

```bash
pip install openrouteservice geopy folium pandas requests
