# 🧭 Integrated/Unified Route Planner (Land & Air)

This application is a comprehensive **route planning tool for India**, supporting both **land routes** (by car) and **air routes** (via live flight data). It provides optimized routes using Dijkstra's algorithm and integrates live data from the **Aviationstack** and **OpenRouteService** APIs.

## 🚀 Features

### ✈️ Air Routing
- Live data from **Aviationstack API**
- Supports:
  - Direct flights
  - One-stop connecting flights (with layover time consideration)
  - Shortest hop path via Dijkstra’s algorithm
- Displays:
  - Airline, flight number, terminals, scheduled times
  - Duration, aircraft model, status

### 🚗 Land Routing
- Powered by **OpenRouteService API** + **Geopy**
- Supports:
  - Dijkstra’s algorithm over real driving routes
  - Multiple alternative driving routes
- Analyzes:
  - Traffic delay simulation
  - Estimated time, fuel consumption, and cost
- Interactive map with traffic-aware segments (color-coded)

## 🖥️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python
- **APIs Used**:
  - [Aviationstack](https://aviationstack.com/) (Live flight data)
  - [OpenRouteService](https://openrouteservice.org/) (Road routing)
- **Other Libraries**: `geopy`, `folium`, `pandas`, `heapq`, `math`, `datetime`
