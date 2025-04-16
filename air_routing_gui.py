import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime, timedelta
import air_routing
import threading
import time

class AirRoutingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Air Routing Search")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Configure style
        self.setup_styles()
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20", style="Main.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header_frame = ttk.Frame(main_frame, style="Header.TFrame")
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        header_label = ttk.Label(
            header_frame, 
            text="✈️ Air Routing Search", 
            font=("Helvetica", 24, "bold"),
            style="Header.TLabel"
        )
        header_label.pack(pady=10)
        
        # Airport input section
        airport_frame = ttk.LabelFrame(
            main_frame, 
            text="Airport Information", 
            padding="15",
            style="Card.TLabelframe"
        )
        airport_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Departure airport
        dep_frame = ttk.Frame(airport_frame)
        dep_frame.grid(row=0, column=0, sticky=tk.W, padx=10)
        
        ttk.Label(
            dep_frame, 
            text="Departure Airport (IATA):", 
            style="Card.TLabel"
        ).grid(row=0, column=0, sticky=tk.W)
        
        self.dep_iata = ttk.Entry(
            dep_frame, 
            width=10, 
            font=("Courier", 12),
            style="Card.TEntry"
        )
        self.dep_iata.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Arrival airport
        arr_frame = ttk.Frame(airport_frame)
        arr_frame.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(
            arr_frame, 
            text="Arrival Airport (IATA):", 
            style="Card.TLabel"
        ).grid(row=0, column=0, sticky=tk.W)
        
        self.arr_iata = ttk.Entry(
            arr_frame, 
            width=10, 
            font=("Courier", 12),
            style="Card.TEntry"
        )
        self.arr_iata.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Search buttons
        button_frame = ttk.Frame(main_frame, style="Button.TFrame")
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        self.direct_button = ttk.Button(
            button_frame, 
            text="🔍 Search Direct Flights", 
            command=self.search_direct_flights,
            style="Action.TButton"
        )
        self.direct_button.grid(row=0, column=0, padx=10)
        
        self.connecting_button = ttk.Button(
            button_frame, 
            text="🔄 Search Connecting Flights", 
            command=self.search_connecting_flights,
            style="Action.TButton"
        )
        self.connecting_button.grid(row=0, column=1, padx=10)
        
        # Loading indicator
        self.loading_frame = ttk.Frame(main_frame, style="Loading.TFrame")
        self.loading_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.loading_label = ttk.Label(
            self.loading_frame, 
            text="Searching flights...", 
            style="Loading.TLabel"
        )
        self.loading_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(
            self.loading_frame, 
            mode='indeterminate', 
            length=200,
            style="Loading.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(side=tk.LEFT, padx=5)
        
        # Hide loading indicator initially
        self.loading_frame.grid_remove()
        
        # Results section
        results_frame = ttk.LabelFrame(
            main_frame, 
            text="Search Results", 
            padding="15",
            style="Card.TLabelframe"
        )
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            width=80, 
            height=20,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#333333"
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Initialize flight API
        self.flight_api = air_routing.FlightAPI()
        
        # Add animation effects
        self.animate_header(header_label)
        
    def setup_styles(self):
        """Configure custom styles for the GUI"""
        style = ttk.Style()
        
        # Main frame style
        style.configure("Main.TFrame", background="#f0f0f0")
        
        # Header styles
        style.configure("Header.TFrame", background="#f0f0f0")
        style.configure("Header.TLabel", background="#f0f0f0", foreground="#2c3e50")
        
        # Card styles
        style.configure("Card.TLabelframe", background="#ffffff", foreground="#2c3e50")
        style.configure("Card.TLabelframe.Label", background="#ffffff", foreground="#2c3e50", font=("Helvetica", 10, "bold"))
        style.configure("Card.TLabel", background="#ffffff", foreground="#2c3e50")
        style.configure("Card.TEntry", fieldbackground="#ffffff", foreground="#2c3e50")
        
        # Button styles
        style.configure("Button.TFrame", background="#f0f0f0")
        style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=10)
        
        # Loading styles
        style.configure("Loading.TFrame", background="#f0f0f0")
        style.configure("Loading.TLabel", background="#f0f0f0", foreground="#2c3e50", font=("Helvetica", 10))
        style.configure("Loading.Horizontal.TProgressbar", background="#3498db", troughcolor="#ecf0f1", bordercolor="#3498db")
        
    def animate_header(self, widget):
        """Animate the header with a fade-in effect"""
        widget.configure(foreground="#3498db")
        self.root.after(500, lambda: widget.configure(foreground="#2c3e50"))
        
    def show_loading(self, message="Searching flights..."):
        """Show the loading indicator with animation"""
        self.loading_label.configure(text=message)
        self.loading_frame.grid()
        self.progress_bar.start(10)
        self.direct_button.configure(state="disabled")
        self.connecting_button.configure(state="disabled")
        self.root.update()
        
    def hide_loading(self):
        """Hide the loading indicator"""
        self.progress_bar.stop()
        self.loading_frame.grid_remove()
        self.direct_button.configure(state="normal")
        self.connecting_button.configure(state="normal")
        self.root.update()
        
    def search_direct_flights(self):
        """Search for direct flights with loading indicator"""
        dep_iata = self.dep_iata.get().upper()
        arr_iata = self.arr_iata.get().upper()
        
        if not dep_iata or not arr_iata:
            messagebox.showerror("Input Error", "Please enter both departure and arrival airport codes")
            return
            
        self.clear_results()
        self.display_message("🔎 Searching for direct flights...")
        
        # Run search in a separate thread to avoid freezing the UI
        self.show_loading("Searching direct flights...")
        threading.Thread(target=self._search_direct_flights_thread, args=(dep_iata, arr_iata)).start()
        
    def _search_direct_flights_thread(self, dep_iata, arr_iata):
        """Thread function for direct flight search"""
        try:
            direct_flights = air_routing.get_direct_flights(dep_iata, arr_iata)
            
            # Update UI in the main thread
            self.root.after(0, lambda: self._display_direct_flights(direct_flights))
        except Exception as e:
            self.root.after(0, lambda: self.display_error(f"Error searching flights: {e}"))
        finally:
            self.root.after(0, self.hide_loading)
            
    def _display_direct_flights(self, direct_flights):
        """Display direct flight results"""
        if not direct_flights.empty:
            self.display_message("\nDirect Flights Found:")
            for _, flight in direct_flights.iterrows():
                self.display_message(self.format_flight_info(flight))
                self.display_message("-" * 50)
        else:
            self.display_message("No direct flights found")

    def search_connecting_flights(self):
        """Search for connecting flights with loading indicator"""
        dep_iata = self.dep_iata.get().upper()
        arr_iata = self.arr_iata.get().upper()
        
        if not dep_iata or not arr_iata:
            messagebox.showerror("Input Error", "Please enter both departure and arrival airport codes")
            return
            
        self.clear_results()
        self.display_message("🔁 Searching for connecting flights...")
        
        # Run search in a separate thread to avoid freezing the UI
        self.show_loading("Searching connecting flights...")
        threading.Thread(target=self._search_connecting_flights_thread, args=(dep_iata, arr_iata)).start()
        
    def _search_connecting_flights_thread(self, dep_iata, arr_iata):
        """Thread function for connecting flight search"""
        try:
            connections = air_routing.find_connecting_flights(dep_iata, arr_iata)
            
            # Update UI in the main thread
            self.root.after(0, lambda: self._display_connections(connections))
        except Exception as e:
            self.root.after(0, lambda: self.display_error(f"Error searching flights: {e}"))
        finally:
            self.root.after(0, self.hide_loading)
            
    def _display_connections(self, connections):
        """Display connecting flight results"""
        self.display_connections(connections)

    def format_flight_info(self, flight):
        """Format flight information for display"""
        try:
            airline = flight.get('airline', {}).get('name', 'Unknown Airline')
            flight_number = flight.get('flight', {}).get('number', 'N/A')
            
            departure = flight.get('departure', {})
            dep_airport = departure.get('iata', 'N/A')
            dep_time = departure.get('scheduled', 'N/A')
            dep_terminal = departure.get('terminal', 'N/A')
            if dep_time != 'N/A':
                dep_time = datetime.fromisoformat(dep_time.replace('Z', '+00:00')).strftime('%H:%M')
            
            arrival = flight.get('arrival', {})
            arr_airport = arrival.get('iata', 'N/A')
            arr_time = arrival.get('scheduled', 'N/A')
            arr_terminal = arrival.get('terminal', 'N/A')
            if arr_time != 'N/A':
                arr_time = datetime.fromisoformat(arr_time.replace('Z', '+00:00')).strftime('%H:%M')
            
            info = f"{airline} {flight_number}\n"
            info += f"  {dep_airport} → {arr_airport}\n"
            info += f"  Departure: {dep_time} (Terminal {dep_terminal})\n"
            info += f"  Arrival: {arr_time} (Terminal {arr_terminal})\n"
            
            status = flight.get('flight_status', '')
            if status:
                info += f"  Status: {status}\n"
                
            aircraft = flight.get('aircraft', 'N/A')
            if aircraft != 'N/A':
                info += f"  Aircraft: {aircraft}\n"
                
            duration = flight.get('duration', 'N/A')
            if duration != 'N/A':
                info += f"  Duration: {duration} minutes\n"
                
            return info
            
        except Exception as e:
            self.display_error(f"Error formatting flight info: {e}")
            return "Error displaying flight information"

    def display_connections(self, connections):
        """Display formatted connecting flight information"""
        if not connections:
            self.display_message("No connecting flights found")
            return

        for i, conn in enumerate(connections, 1):
            self.display_message(f"\nConnection Option {i}:")
            self.display_message("First Flight:")
            self.display_message(self.format_flight_info(conn['first_flight']))
            self.display_message(f"Connection at {conn['connection_airport']} ({conn['layover_duration']})")
            self.display_message("Second Flight:")
            self.display_message(self.format_flight_info(conn['second_flight']))
            self.display_message("-" * 50)

    def display_message(self, message):
        """Display a message in the results text area"""
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)

    def display_error(self, message):
        """Display an error message in the results text area"""
        self.results_text.insert(tk.END, f"Error: {message}\n", "error")
        self.results_text.see(tk.END)

    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = AirRoutingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 