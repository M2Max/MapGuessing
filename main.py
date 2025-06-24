import sys
from src.restaurant_list import PlaceSearcher
from src.distance_calculator import DistanceCalculator
from src.filter_values import PlaceFilter

def get_float(prompt, default=None):
    while True:
        val = input(f"{prompt} [{default if default is not None else ''}]: ").strip()
        if not val and default is not None:
            return default
        try:
            return float(val)
        except ValueError:
            print("Please enter a valid number.")

def get_int(prompt, default=None):
    while True:
        val = input(f"{prompt} [{default if default is not None else ''}]: ").strip()
        if not val and default is not None:
            return default
        try:
            return int(val)
        except ValueError:
            print("Please enter a valid integer.")

def main():
    print("=== MapGuessing Place Search ===")
    api_key = input("Enter your Google Maps API key: ").strip()
    lat = get_float("Enter center latitude")
    lng = get_float("Enter center longitude")
    diameter_km = get_float("Enter search diameter in km", 10)
    radius_m = int(diameter_km * 1000 / 2)
    min_km = get_float("Minimum distance (km) for filtering", 0)
    max_km = get_float("Maximum distance (km) for filtering", 100)
    min_min = get_int("Minimum travel time (minutes) for filtering", 0)
    max_min = get_int("Maximum travel time (minutes) for filtering", 120)

    # Search for places
    searcher = PlaceSearcher(api_key)
    print("Searching for places...")
    places = searcher.search(lat, lng, radius_m)
    print(f"Found {len(places)} places. Calculating distances...")

    # Calculate distances
    calculator = DistanceCalculator(api_key, lat, lng)
    places_with_dist = calculator.calculate_for_places(places)

    # Filter places
    filterer = PlaceFilter(min_km, max_km, min_min, max_min)
    filtered = filterer.filter(places_with_dist)
    print(f"Filtered to {len(filtered)} places:")
    for p in filtered:
        print(f"{p.get('name')} - {p.get('address')} | {p.get('distance_km')} km | {p.get('duration_text')}")

if __name__ == "__main__":
    main()
