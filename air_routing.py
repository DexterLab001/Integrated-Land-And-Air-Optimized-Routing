import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import heapq
from collections import defaultdict
import os
import time

# --- CONFIGURATION ---
AVIATION_STACK_KEY = os.getenv('AVIATION_STACK_KEY', 'a2f8de218fb5016b41c2e50740ba5740')
AVIATION_STACK_URL = "http://api.aviationstack.com/v1"
REQUEST_DELAY = 1  # seconds between API requests to avoid rate limiting
MAX_CONNECTION_DEPTH = 2

class FlightAPI:
    def __init__(self, max_requests=5):
        self.aviation_stack_token = AVIATION_STACK_KEY
        self.last_request_time = 0
        self.request_count = 0
        self.max_requests = max_requests

    def get_flights(self, dep_iata, arr_iata=None):
        if self.request_count >= self.max_requests:
            print(f"[INFO] Request limit of {self.max_requests} reached.")
            return pd.DataFrame()

        time_since_last = time.time() - self.last_request_time
        if time_since_last < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - time_since_last)

        params = {
            'access_key': self.aviation_stack_token,
            'limit': 100,
            'flight_status': 'active'
        }
        if dep_iata:
            params['dep_iata'] = dep_iata
        if arr_iata:
            params['arr_iata'] = arr_iata

        try:
            response = requests.get(f"{AVIATION_STACK_URL}/flights", params=params)
            self.last_request_time = time.time()
            self.request_count += 1
            response.raise_for_status()
            data = response.json()
            if data.get('error'):
                print(f"API Error: {data['error']['message']}")
                return pd.DataFrame()
            return pd.DataFrame(data.get('data', []))
        except Exception as e:
            print(f"API request failed: {e}")
            return pd.DataFrame()

class FlightPathFinder:
    def __init__(self, flight_api):
        self.api = flight_api
        self.graph = defaultdict(dict)
        self.request_cache = {}

    def build_graph(self, origin, destination):
        self._build_graph_recursive(origin, destination, current_depth=0)

    def _build_graph_recursive(self, current_airport, destination, current_depth):
        if current_depth >= MAX_CONNECTION_DEPTH:
            return

        cache_key = f"{current_airport}-{destination if current_depth == MAX_CONNECTION_DEPTH-1 else ''}"
        if cache_key in self.request_cache:
            flights = self.request_cache[cache_key]
        else:
            flights = self.api.get_flights(current_airport, destination if current_depth == MAX_CONNECTION_DEPTH-1 else None)
            self.request_cache[cache_key] = flights

        for _, flight in flights.iterrows():
            arr_iata = flight.get('arrival', {}).get('iata')
            if not arr_iata:
                continue

            self.graph[current_airport][arr_iata] = {
                'flight': flight,
                'weight': 1
            }

            if arr_iata != destination and arr_iata not in self.graph:
                self._build_graph_recursive(arr_iata, destination, current_depth+1)

def find_shortest_path(finder, origin, destination):
    if origin not in finder.graph:
        finder.build_graph(origin, destination)

    distances = {airport: float('infinity') for airport in finder.graph}
    distances[origin] = 0
    previous_nodes = {airport: None for airport in finder.graph}
    pq = [(0, origin)]

    while pq:
        current_distance, current_airport = heapq.heappop(pq)
        if current_airport == destination:
            break
        if current_distance > distances[current_airport]:
            continue
        for neighbor, data in finder.graph[current_airport].items():
            distance = current_distance + data['weight']
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = (current_airport, data['flight'])
                heapq.heappush(pq, (distance, neighbor))

    if previous_nodes[destination] is None:
        return [], float('infinity')

    path = []
    current = destination
    while previous_nodes[current] is not None:
        prev_airport, flight = previous_nodes[current]
        path.insert(0, (prev_airport, current, flight))
        current = prev_airport
    return path, distances.get(destination, float('infinity'))

def get_direct_flights(dep_iata, arr_iata, api):
    return api.get_flights(dep_iata, arr_iata)

def find_connecting_flights(dep_iata, arr_iata, api):
    departures = api.get_flights(dep_iata)
    connections = []
    if departures.empty:
        return connections

    for _, first_leg in departures.iterrows():
        try:
            connection_airport = first_leg.get('arrival', {}).get('iata')
            if not connection_airport or connection_airport == arr_iata:
                continue
            second_legs = api.get_flights(connection_airport, arr_iata)
            for _, second_leg in second_legs.iterrows():
                first_arr_time = first_leg.get('arrival', {}).get('scheduled')
                second_dep_time = second_leg.get('departure', {}).get('scheduled')
                if first_arr_time and second_dep_time:
                    first_arr = datetime.fromisoformat(first_arr_time.replace('Z', '+00:00'))
                    second_dep = datetime.fromisoformat(second_dep_time.replace('Z', '+00:00'))
                    layover = second_dep - first_arr
                    if timedelta(hours=1) <= layover <= timedelta(hours=5):
                        connections.append({
                            'first_flight': first_leg,
                            'second_flight': second_leg,
                            'connection_airport': connection_airport,
                            'layover_duration': layover
                        })
        except Exception:
            continue
    return connections

def display_flight_info(flight) -> str:
    try:
        if flight is None:
            return ""
            
        # Get flight details with fallbacks
        airline = flight.get('airline', {}).get('name', 'Unknown Airline')
        flight_number = flight.get('flight', {}).get('number', 'N/A')
        
        # Departure info
        departure = flight.get('departure', {})
        dep_airport = departure.get('iata', 'N/A')
        dep_time_str = departure.get('scheduled', 'N/A')
        dep_terminal = departure.get('terminal', 'N/A')
        
        # Arrival info
        arrival = flight.get('arrival', {})
        arr_airport = arrival.get('iata', 'N/A')
        arr_time_str = arrival.get('scheduled', 'N/A')
        arr_terminal = arrival.get('terminal', 'N/A')
        
        # Other details
        status = flight.get('flight_status', 'N/A')
        aircraft = flight.get('aircraft', {}).get('model', 'Not specified')
        
        # Calculate duration
        duration = 'N/A'
        if dep_time_str != 'N/A' and arr_time_str != 'N/A':
            try:
                dep_time = datetime.fromisoformat(dep_time_str.replace('Z', '+00:00'))
                arr_time = datetime.fromisoformat(arr_time_str.replace('Z', '+00:00'))
                delta = arr_time - dep_time
                total_minutes = int(delta.total_seconds() / 60)
                hours = total_minutes // 60
                minutes = total_minutes % 60
                duration = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                dep_time_str = dep_time.strftime('%H:%M')
                arr_time_str = arr_time.strftime('%H:%M')
            except Exception:
                pass

        return f"""
### ✈️ {airline} {flight_number}
**Departure**  
🛫 {dep_airport} • Terminal {dep_terminal} • {dep_time_str}  

**Arrival**  
🛬 {arr_airport} • Terminal {arr_terminal} • {arr_time_str}  

**Details**  
📌 Status: {status}  
✈️ Aircraft: {aircraft}  
⏱ Duration: {duration}  

---
"""
    except Exception as e:
        print(f"Error formatting flight info: {e}")
        return ""

def format_connections(connections) -> list:
    formatted = []
    for i, conn in enumerate(connections, 1):
        try:
            if not conn or 'first_flight' not in conn or 'second_flight' not in conn:
                continue
                
            info = f"### ✈️ Connection Option {i}\n"
            info += f"**Layover at {conn.get('connection_airport', 'Unknown')}** — ⏱ {conn.get('layover_duration', 'N/A')}\n"
            info += f"**First Flight:**\n{display_flight_info(conn['first_flight'])}\n"
            info += f"**Second Flight:**\n{display_flight_info(conn['second_flight'])}\n"
            formatted.append(info)
        except Exception as e:
            print(f"Error formatting connection {i}: {e}")
            continue
    return formatted

def format_dijkstra_path(path, total_weight) -> str:
    if not path:
        return "❌ No route found."
    info = f"### ✅ Shortest Path Found ({len(path)} segments)\n"
    for i, (origin, dest, flight) in enumerate(path, 1):
        info += f"**Segment {i}:** {origin} → {dest}\n"
        info += display_flight_info(flight) + "\n\n"
    info += f"🔁 Total Hops: {total_weight}"
    return info
