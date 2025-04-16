import requests
import pandas as pd
from datetime import datetime, timedelta
import json

# --- CONFIGURATION ---
AVIATION_STACK_KEY = "0a0719bce0dbab1b05b9e70e14a5e172"
AVIATION_STACK_URL = "http://api.aviationstack.com/v1"

class FlightAPI:
    def __init__(self):
        self.aviation_stack_token = AVIATION_STACK_KEY

    def get_flights(self, dep_iata, arr_iata=None):
        """Get flights from Aviation Stack"""
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
            response.raise_for_status()
            data = response.json()
            
            if data.get('error'):
                print(f"Aviation Stack API Error: {data['error']['message']}")
                return pd.DataFrame()
                
            flights = data.get('data', [])
            return pd.DataFrame(flights)
        except Exception as e:
            print(f"Error fetching flights: {e}")
            return pd.DataFrame()

def get_flights_by_airport(airport_iata, flight_type='departure'):
    """Get flights (departures or arrivals) for a specific airport"""
    api = FlightAPI()
    return api.get_flights(airport_iata)

def get_direct_flights(dep_iata, arr_iata):
    """Get direct flights between two airports"""
    api = FlightAPI()
    return api.get_flights(dep_iata, arr_iata)

def find_connecting_flights(dep_iata, arr_iata):
    """Find connecting flights with layovers between 1-5 hours"""
    departures = get_flights_by_airport(dep_iata, 'departure')
    connections = []

    if departures.empty:
        print("No departure flights found")
        return connections

    for _, first_leg in departures.iterrows():
        try:
            connection_airport = first_leg.get('arrival', {}).get('iata')
            
            if not connection_airport or connection_airport == arr_iata:
                continue
                
            # Get flights from connection airport to destination
            second_legs = get_flights_by_airport(connection_airport, 'departure')
            
            for _, second_leg in second_legs.iterrows():
                if second_leg.get('arrival', {}).get('iata') == arr_iata:
                    # Get scheduled times
                    first_arr_time = first_leg.get('arrival', {}).get('scheduled')
                    second_dep_time = second_leg.get('departure', {}).get('scheduled')
                    
                    if first_arr_time and second_dep_time:
                        # Calculate layover duration
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
        except Exception as e:
            print(f"Error processing flight connection: {e}")
            continue

    return connections

def display_flight_info(flight):
    """Display formatted flight information"""
    try:
        airline = flight.get('airline', {}).get('name', 'Unknown Airline')
        flight_number = flight.get('flight', {}).get('number', 'N/A')
        
        # Get departure information
        departure = flight.get('departure', {})
        dep_airport = departure.get('iata', 'N/A')
        dep_time = departure.get('scheduled', 'N/A')
        dep_terminal = departure.get('terminal', 'N/A')
        if dep_time != 'N/A':
            dep_time = datetime.fromisoformat(dep_time.replace('Z', '+00:00')).strftime('%H:%M')
        
        # Get arrival information
        arrival = flight.get('arrival', {})
        arr_airport = arrival.get('iata', 'N/A')
        arr_time = arrival.get('scheduled', 'N/A')
        arr_terminal = arrival.get('terminal', 'N/A')
        if arr_time != 'N/A':
            arr_time = datetime.fromisoformat(arr_time.replace('Z', '+00:00')).strftime('%H:%M')
        
        print(f"{airline} {flight_number}")
        print(f"  {dep_airport} → {arr_airport}")
        print(f"  Departure: {dep_time} (Terminal {dep_terminal})")
        print(f"  Arrival: {arr_time} (Terminal {arr_terminal})")
        
        # Print additional information if available
        status = flight.get('flight_status', '')
        if status:
            print(f"  Status: {status}")
            
        # Print aircraft information if available
        aircraft = flight.get('aircraft', 'N/A')
        if aircraft != 'N/A':
            print(f"  Aircraft: {aircraft}")
            
        # Print duration if available
        duration = flight.get('duration', 'N/A')
        if duration != 'N/A':
            print(f"  Duration: {duration} minutes")
            
    except Exception as e:
        print(f"Error displaying flight info: {e}")
        print("Raw flight data:", json.dumps(flight, indent=2))

def display_connections(connections):
    """Display formatted connecting flight information"""
    if not connections:
        print("No connecting flights found")
        return

    for i, conn in enumerate(connections, 1):
        print(f"\nConnection Option {i}:")
        print("First Flight:")
        display_flight_info(conn['first_flight'])
        print(f"Connection at {conn['connection_airport']} ({conn['layover_duration']})")
        print("Second Flight:")
        display_flight_info(conn['second_flight'])
        print("-" * 50)

def main():
    """Main function to search for flights"""
    print("\n=== Flight Search (Current Day Only) ===")
    dep_iata = input("Enter departure airport IATA code (e.g., DEL): ").upper()
    arr_iata = input("Enter arrival airport IATA code (e.g., BOM): ").upper()

    print("\n🔎 Searching for direct flights...")
    direct_flights = get_direct_flights(dep_iata, arr_iata)
    
    if not direct_flights.empty:
        print("\nDirect Flights Found:")
        for _, flight in direct_flights.iterrows():
            display_flight_info(flight)
            print("-" * 50)
    else:
        print("No direct flights found")

    print("\n🔁 Searching for connecting flights...")
    connections = find_connecting_flights(dep_iata, arr_iata)
    display_connections(connections)

if __name__ == "__main__":
    main() 