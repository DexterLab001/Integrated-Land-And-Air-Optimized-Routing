
import openrouteservice
from geopy.geocoders import Nominatim
import folium
import math
import heapq
import random

# ====== CONFIGURATION ======
ORS_API_KEY = '5b3ce3597851110001cf6248788d76fba8b84392a515456e938e8834'
client = openrouteservice.Client(key=ORS_API_KEY)
geolocator = Nominatim(user_agent="land_routing_app")

# ====== FUNCTIONS ======

def get_coordinates(place):
    location = geolocator.geocode(place)
    if location:
        return (location.latitude, location.longitude)
    else:
        raise ValueError(f"Location not found: {place}")

def haversine(coord1, coord2):
    R = 6371  # Earth radius in km
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_route_geometry(start_coords, end_coords):
    try:
        response = client.directions(
            coordinates=[start_coords[::-1], end_coords[::-1]],
            profile='driving-car',
            format='geojson',
            alternative_routes={"share_factor": 0.6, "target_count": 2}
        )

        routes = []
        for feature in response['features']:
            route_coords = [(lat, lon) for lon, lat in feature['geometry']['coordinates']]
            routes.append(route_coords)

        return routes
    except Exception as e:
        print(f"Error fetching routes: {e}")
        return []

def build_graph(coords):
    graph = {}
    for i in range(len(coords) - 1):
        a = coords[i]
        b = coords[i + 1]
        dist = haversine(a, b)
        graph.setdefault(a, {})[b] = dist
        graph.setdefault(b, {})[a] = dist
    return graph

def dijkstra(graph, start, end):
    queue = [(0, start)]
    distances = {node: float('inf') for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0

    while queue:
        current_dist, current_node = heapq.heappop(queue)
        if current_node == end:
            break

        for neighbor, weight in graph[current_node].items():
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    # Reconstruct path
    path = []
    node = end
    while node is not None:
        path.insert(0, node)
        node = previous[node]

    return path, distances[end]

def get_traffic_data(coords):
    traffic = []
    for i, coord in enumerate(coords[:-1]):
        if i % 10 == 0:
            traffic.append(random.uniform(0.7, 1.0))
        else:
            traffic.append(random.uniform(0.1, 0.3))
    return traffic

def calculate_metrics(distance_km, traffic_factor=1.0):
    base_speed_kmph = 50
    efficiency_kmpl = 15
    speed_kmph = base_speed_kmph * (1 - traffic_factor*0.4)
    time_hr = distance_km / speed_kmph
    fuel_l = distance_km / efficiency_kmpl
    return time_hr, fuel_l, speed_kmph

def plot_route(routes, traffic_data_list):
    m = folium.Map(location=routes[0][0], zoom_start=7)
    for idx, route in enumerate(routes):
        traffic_data = traffic_data_list[idx]
        for i in range(len(route) - 1):
            segment = [route[i], route[i+1]]
            traffic = traffic_data[i]
            color = 'green' if traffic < 0.4 else 'orange' if traffic < 0.7 else 'red'
            folium.PolyLine(segment, color=color, weight=5, opacity=0.8).add_to(m)

        folium.Marker(route[0], popup="Start", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(route[-1], popup="End", icon=folium.Icon(color='red')).add_to(m)

    m.save("dijkstra_route_map.html")
    print("Map saved to dijkstra_route_map.html")

# ====== MAIN FUNCTION ======

def main():
    print("=== India Land Route Planner with Dijkstra ===")
    start_city = input("Enter Start City: ")
    end_city = input("Enter End City: ")

    try:
        start_coords = get_coordinates(start_city)
        end_coords = get_coordinates(end_city)
        print(f"Fetching routes from {start_city} to {end_city}...")

        routes = get_route_geometry(start_coords, end_coords)
        if not routes:
            print("No routes found.")
            return

        traffic_data_list = []
        for route in routes:
            traffic_data = get_traffic_data(route)
            traffic_data_list.append(traffic_data)

            graph = build_graph(route)
            path, distance = dijkstra(graph, route[0], route[-1])
            time, fuel, speed = calculate_metrics(distance, sum(traffic_data)/len(traffic_data))

            print(f"\n=== ROUTE OPTION {routes.index(route)+1} ===")
            print(f"Distance: {distance:.2f} km")
            print(f"Estimated Time: {time:.2f} hrs (avg speed: {speed:.1f} km/h)")
            print(f"Fuel Usage: {fuel:.2f} L")

        plot_route(routes, traffic_data_list)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
