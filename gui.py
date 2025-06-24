import tkinter as tk
from tkinter import ttk, messagebox
from src.restaurant_list import PlaceSearcher
from src.distance_calculator import DistanceCalculator
from src.filter_values import PlaceFilter

class MapGuessingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MapGuessing Place Search")
        self.geometry("500x500")
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)
        row = 0
        # API Key
        ttk.Label(frm, text="Google Maps API Key:").grid(row=row, column=0, sticky=tk.W)
        self.api_key = ttk.Entry(frm, width=40, show="*")
        self.api_key.grid(row=row, column=1)
        row += 1
        # Latitude
        ttk.Label(frm, text="Center Latitude:").grid(row=row, column=0, sticky=tk.W)
        self.lat = ttk.Entry(frm)
        self.lat.grid(row=row, column=1)
        row += 1
        # Longitude
        ttk.Label(frm, text="Center Longitude:").grid(row=row, column=0, sticky=tk.W)
        self.lng = ttk.Entry(frm)
        self.lng.grid(row=row, column=1)
        row += 1
        # Diameter
        ttk.Label(frm, text="Search Diameter (km):").grid(row=row, column=0, sticky=tk.W)
        self.diameter = ttk.Entry(frm)
        self.diameter.insert(0, "10")
        self.diameter.grid(row=row, column=1)
        row += 1
        # Min/Max Distance
        ttk.Label(frm, text="Min Distance (km):").grid(row=row, column=0, sticky=tk.W)
        self.min_km = ttk.Entry(frm)
        self.min_km.insert(0, "0")
        self.min_km.grid(row=row, column=1)
        row += 1
        ttk.Label(frm, text="Max Distance (km):").grid(row=row, column=0, sticky=tk.W)
        self.max_km = ttk.Entry(frm)
        self.max_km.insert(0, "100")
        self.max_km.grid(row=row, column=1)
        row += 1
        # Min/Max Duration
        ttk.Label(frm, text="Min Travel Time (min):").grid(row=row, column=0, sticky=tk.W)
        self.min_min = ttk.Entry(frm)
        self.min_min.insert(0, "0")
        self.min_min.grid(row=row, column=1)
        row += 1
        ttk.Label(frm, text="Max Travel Time (min):").grid(row=row, column=0, sticky=tk.W)
        self.max_min = ttk.Entry(frm)
        self.max_min.insert(0, "120")
        self.max_min.grid(row=row, column=1)
        row += 1
        # Search Button
        self.search_btn = ttk.Button(frm, text="Search", command=self.run_search)
        self.search_btn.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        # Results
        self.results = tk.Text(frm, height=15, width=60)
        self.results.grid(row=row, column=0, columnspan=2)

    def run_search(self):
        try:
            api_key = self.api_key.get().strip()
            lat = float(self.lat.get())
            lng = float(self.lng.get())
            diameter_km = float(self.diameter.get())
            radius_m = int(diameter_km * 1000 / 2)
            min_km = float(self.min_km.get())
            max_km = float(self.max_km.get())
            min_min = int(self.min_min.get())
            max_min = int(self.max_min.get())
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return
        self.results.delete(1.0, tk.END)
        self.results.insert(tk.END, "Searching for places...\n")
        self.update()
        try:
            searcher = PlaceSearcher(api_key)
            places = searcher.search(lat, lng, radius_m)
            self.results.insert(tk.END, f"Found {len(places)} places. Calculating distances...\n")
            self.update()
            calculator = DistanceCalculator(api_key, lat, lng)
            places_with_dist = calculator.calculate_for_places(places)
            filterer = PlaceFilter(min_km, max_km, min_min, max_min)
            filtered = filterer.filter(places_with_dist)
            self.results.insert(tk.END, f"Filtered to {len(filtered)} places:\n")
            for p in filtered:
                self.results.insert(tk.END, f"{p.get('name')} - {p.get('address')} | {p.get('distance_km')} km | {p.get('duration_text')}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = MapGuessingApp()
    app.mainloop()
