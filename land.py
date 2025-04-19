import tkinter as tk
from tkinter import messagebox
from openrouteservice import Client
from geopy.geocoders import Nominatim
import folium
import webbrowser
import os
from datetime import datetime

# Replace with your actual API key
ORS_API_KEY = "5b3ce3597851110001cf6248788d76fba8b84392a515456e938e8834"
client = Client(key=ORS_API_KEY)
geolocator = Nominatim(user_agent="land_route_gui")

def geocode_location(location_name):
    try:
        location = geolocator.geocode(location_name)
        return [location.longitude, location.latitude]
    except:
        return None

def get_route_info(source, destination):
    coords = [source, destination]
    try:
        route = client.directions(coords, format='geojson')
        distance_km = route['features'][0]['properties']['segments'][0]['distance'] / 1000  # meters to km
        duration_min = route['features'][0]['properties']['segments'][0]['duration'] / 60   # seconds to minutes
        geometry = route['features'][0]['geometry']['coordinates']
        return round(distance_km, 2), round(duration_min, 2), geometry
    except Exception as e:
        print("Error:", e)
        return None, None, None
def show_map(route_geometry, source_coords, dest_coords):
    mid_lat = (source_coords[1] + dest_coords[1]) / 2
    mid_lon = (source_coords[0] + dest_coords[0]) / 2
    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=10)

    # Convert geometry coords from [lon, lat] to [lat, lon]
    route_latlon = [(coord[1], coord[0]) for coord in route_geometry]
    folium.PolyLine(route_latlon, color="blue", weight=5).add_to(m)

    folium.Marker([source_coords[1], source_coords[0]], tooltip="Source", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([dest_coords[1], dest_coords[0]], tooltip="Destination", icon=folium.Icon(color='red')).add_to(m)

    map_file = f"route_map_{datetime.now().strftime('%H%M%S')}.html"
    m.save(map_file)
    webbrowser.open('file://' + os.path.realpath(map_file))
def calculate_route():
    source_name = source_entry.get()
    dest_name = dest_entry.get()

    source_coords = geocode_location(source_name)
    dest_coords = geocode_location(dest_name)

    if not source_coords or not dest_coords:
        messagebox.showerror("Error", "Could not geocode one or both locations.")
        return

    distance, duration, geometry = get_route_info(source_coords, dest_coords)

    if distance is None or duration is None or geometry is None:
        messagebox.showerror("Error", "Could not retrieve route info.")
        return

    output_label.config(text=f"Distance: {distance} km\nDuration: {duration} minutes")
    show_map(geometry, source_coords, dest_coords)

# GUI Setup
root = tk.Tk()
root.title("Land Routing (Road/Rail) GUI")
root.geometry("400x300")
root.configure(bg="#f0f8ff")

tk.Label(root, text="Enter Source:", font=("Arial", 12), bg="#f0f8ff").pack(pady=5)
source_entry = tk.Entry(root, font=("Arial", 12), width=30)
source_entry.pack()

tk.Label(root, text="Enter Destination:", font=("Arial", 12), bg="#f0f8ff").pack(pady=5)
dest_entry = tk.Entry(root, font=("Arial", 12), width=30)
dest_entry.pack()

tk.Button(root, text="Get Route", font=("Arial", 12, "bold"), command=calculate_route, bg="#4682b4", fg="white").pack(pady=20)

output_label = tk.Label(root, text="", font=("Arial", 12), bg="#f0f8ff")
output_label.pack()

root.mainloop()
