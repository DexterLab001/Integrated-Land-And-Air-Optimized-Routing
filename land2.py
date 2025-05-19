import tkinter as tk
from tkinter import messagebox
from openrouteservice import Client
from geopy.geocoders import Nominatim
import folium
import webbrowser
import os
import random
from datetime import datetime

# API Key setup
ORS_API_KEY = "5b3ce3597851110001cf6248788d76fba8b84392a515456e938e8834"  # Replace with your actual ORS key
client = Client(key=ORS_API_KEY)
geolocator = Nominatim(user_agent="land_route_gui")

# Weight parameters
alpha = 1.0     # Distance weight
beta = 2.0      # Time weight
gamma = 1.5     # Traffic delay weight
delta = 0.0     # Flight delay (not used)
epsilon = 1.0   # Fuel cost weight
def compute_weight(distance, time, traffic_delay, fuel_cost):
    return (alpha * distance +
            beta * time +
            gamma * traffic_delay +
            delta * 0 +
            epsilon * fuel_cost)

def geocode_location(location_name):
    try:
        location = geolocator.geocode(location_name)
        return [location.longitude, location.latitude]
    except:
        return None

def get_two_routes(source, destination):
    coords = [source, destination]
    try:
        routes = client.directions(coords, format='geojson',
                                   alternative_routes={"share_factor": 0.6, "target_count": 2}) route_infos = []
        for feature in routes['features']:
            props = feature['properties']['segments'][0]
            distance = props['distance'] / 1000  # in km
            duration = props['duration'] / 60    # in minutes
            geometry = feature['geometry']['coordinates']
            traffic_delay = random.uniform(3, 15)
            fuel_cost = round(distance * 5, 2)
            route_infos.append({
                "distance": round(distance, 2),
                "duration": round(duration, 2),
                "traffic_delay": round(traffic_delay, 2),
                "fuel_cost": fuel_cost,
                "geometry": geometry
            })
        return route_infos
    except Exception as e:
        messagebox.showerror("Route Error", f"Could not fetch route:\n{e}")
        return []
def show_routes_on_map(source, dest, routes, weights):
    mid_lat = (source[1] + dest[1]) / 2
    mid_lon = (source[0] + dest[0]) / 2
    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=10)

    colors = ['blue', 'red']
    for i, route in enumerate(routes):
        coords = [(pt[1], pt[0]) for pt in route['geometry']]
        folium.PolyLine(coords, color=colors[i], weight=5,
                        tooltip=f"Route {i+1} - Weight: {weights[i]:.2f}").add_to(m)

    folium.Marker([source[1], source[0]], tooltip="Source", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([dest[1], dest[0]], tooltip="Destination", icon=folium.Icon(color='red')).add_to(m)

    filename = f"route_map_{datetime.now().strftime('%H%M%S')}.html"
    m.save(filename)
    webbrowser.open('file://' + os.path.realpath(filename))
def find_best_route():
    source_name = src_entry.get()
    dest_name = dest_entry.get()

    source_coords = geocode_location(source_name)
    dest_coords = geocode_location(dest_name)

    if not source_coords or not dest_coords:
        messagebox.showerror("Geocode Error", "Could not find one or both locations.")
        return

    routes = get_two_routes(source_coords, dest_coords)
    if len(routes) < 2:
        messagebox.showerror("Route Error", "Could not retrieve two routes.")
        return

    weights = []
    for r in routes:
        w = compute_weight(r['distance'], r['duration'], r['traffic_delay'], r['fuel_cost'])
        weights.append(w)

    show_routes_on_map(source_coords, dest_coords, routes, weights)

    output = ""
    for i, r in enumerate(routes):
        output += f"Route {i+1}:\n"
        output += f"  Distance: {r['distance']} km\n"
        output += f"  Time: {r['duration']} min\n"
        output += f"  Traffic Delay: {r['traffic_delay']} min\n"
        output += f"  Fuel Cost: ₹{r['fuel_cost']}\n"
        output += f"  Total Weight: {weights[i]:.2f}\n\n"
    messagebox.showinfo("Routes Info", output)
root = tk.Tk()
root.title("Land Routing System")
root.geometry("400x200")

tk.Label(root, text="Source Location:").pack(pady=5)
src_entry = tk.Entry(root, width=40)
src_entry.pack()

tk.Label(root, text="Destination Location:").pack(pady=5)
dest_entry = tk.Entry(root, width=40)
dest_entry.pack()

tk.Button(root, text="Find Best Routes", command=find_best_route).pack(pady=20)

root.mainloop()
