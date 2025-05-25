import streamlit as st
import pandas as pd
from datetime import datetime
from air_routing import FlightAPI, get_direct_flights, find_connecting_flights, FlightPathFinder, find_shortest_path, display_flight_info, format_connections
from land_Routing import get_coordinates, get_route_geometry, get_traffic_data, build_graph, dijkstra, calculate_metrics, plot_route

# --- Streamlit Setup ---
st.set_page_config(page_title="Unified Route Planner", layout="wide")
st.title("🧭 Unified Route Planner: Land & Air")

tab1, tab2 = st.tabs(["🚗 Land Routing", "✈️ Air Routing"])

# ------------------------------
# LAND ROUTING TAB
# ------------------------------
with tab1:
    st.header("🚗 Land Route Planner")

    col1, col2 = st.columns(2)
    with col1:
        start_city = st.text_input("Enter Start City", value="Delhi")
    with col2:
        end_city = st.text_input("Enter End City", value="Mumbai")

    if st.button("Find Land Route"):
        try:
            start_coords = get_coordinates(start_city)
            end_coords = get_coordinates(end_city)
            routes = get_route_geometry(start_coords, end_coords)

            if not routes:
                st.error("No routes found.")
            else:
                traffic_data_list = []
                for idx, route in enumerate(routes):
                    traffic_data = get_traffic_data(route)
                    traffic_data_list.append(traffic_data)

                    graph = build_graph(route)
                    path, distance = dijkstra(graph, route[0], route[-1])
                    avg_traffic = sum(traffic_data)/len(traffic_data)
                    time, fuel, speed, cost = calculate_metrics(distance, avg_traffic)

                    st.subheader(f"🛣️ Route Option {idx+1}")
                    st.markdown(f"- **Distance**: {distance:.2f} km")
                    st.markdown(f"- **Time**: {time:.2f} hours at {speed:.1f} km/h")
                    st.markdown(f"- **Fuel**: {fuel:.2f} L, ₹{cost:.2f}")

                plot_route(routes, traffic_data_list)
                with open("dijkstra_route_map.html", "r") as f:
                    html_data = f.read()
                    st.components.v1.html(html_data, height=500)

        except Exception as e:
            st.error(f"Error: {e}")

# ------------------------------
# AIR ROUTING TAB
# ------------------------------
with tab2:
    st.header("✈️ Air Route Planner")

    col1, col2 = st.columns(2)
    with col1:
        dep_iata = st.text_input("Departure Airport IATA Code", value="DEL").upper()
    with col2:
        arr_iata = st.text_input("Arrival Airport IATA Code", value="BOM").upper()

    if st.button("Find Air Route"):
        api = FlightAPI(max_requests=5)
        
        # Get and display direct flights
        st.subheader("✈️ Direct Flights")
        direct_flights = get_direct_flights(dep_iata, arr_iata, api)
        if not direct_flights.empty:
            for _, flight in direct_flights.iterrows():
                flight_info = display_flight_info(flight)
                if flight_info.strip():
                    st.markdown(flight_info, unsafe_allow_html=True)
                    st.write("---")
        else:
            st.warning("No direct flights found")

        # Get and display connecting flights
        st.subheader("🔁 Connecting Flights")
        connections = find_connecting_flights(dep_iata, arr_iata, api)
        if connections:
            for text in format_connections(connections):
                if text.strip():
                    st.markdown(text, unsafe_allow_html=True)
                    st.write("---")
        else:
            st.warning("No valid connecting flights found")

        st.info(f"🔢 API calls used: {api.request_count}/{api.max_requests}")