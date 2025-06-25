import requests
import time
import csv

# Configuration
API_KEY = "YOUR GOOGLE MAPS API KEY"
LOCATION_LAT = 123  # Example: latitude of the center point
LOCATION_LNG = 123  # Example: longitude of the center point
RADIUS = 15000  # in meters
TYPE = "restaurant"  # Place type
OUTPUT_CSV = "restaurants_nearby.csv"
KEYWORDS = ["agriturismo", "osteria", "hostaria", "trattoria", "podere", "locanda", "cantina", "ristorante", "pizzeria", ""]  # Keywords to include in API calls
PAUSE_BETWEEN_REQUESTS = 2.0  # Seconds pause to respect rate limits


class GoogleMapsClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def get(self, url, params):
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()


class PlaceSearcher:
    def __init__(self, api_key):
        self.client = GoogleMapsClient(api_key)
        self.place_type = "restaurant"
        self.keywords = [
            "agriturismo", "osteria", "hostaria", "trattoria", "podere", "locanda",
            "cantina", "ristorante", "pizzeria", ""
        ]

    def search(self, lat, lng, radius):
        all_places = {}
        for keyword in self.keywords:
            location = f"{lat},{lng}"
            page_token = None
            while True:
                params = {
                    "key": self.client.api_key,
                    "location": location,
                    "radius": radius,
                    "type": self.place_type,
                }
                if keyword:
                    params["keyword"] = keyword
                if page_token:
                    params["pagetoken"] = page_token
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                data = self.client.get(url, params)
                for place in data.get("results", []):
                    # Defensive: skip if lat/lng missing
                    geometry = place.get("geometry", {})
                    loc = geometry.get("location", {})
                    lat_val = loc.get("lat")
                    lng_val = loc.get("lng")
                    if lat_val is None or lng_val is None:
                        continue
                    all_places[place["place_id"]] = {
                        "name": place.get("name"),
                        "address": place.get("vicinity"),
                        "latitude": lat_val,
                        "longitude": lng_val
                    }
                page_token = data.get("next_page_token")
                if not page_token:
                    break
        return list(all_places.values())


def save_to_csv(places, filename):
    """
    Save place data to a CSV file.

    :param places: List of place dicts
    :param filename: Output CSV filename
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Header row
        writer.writerow(["name", "address", "latitude", "longitude", "rating", "user_ratings_total", "place_id"])

        for place in places:
            name = place.get("name")
            address = place.get("vicinity")
            lat = place.get("geometry", {}).get("location", {}).get("lat")
            lng = place.get("geometry", {}).get("location", {}).get("lng")
            rating = place.get("rating")
            user_ratings_total = place.get("user_ratings_total")
            place_id = place.get("place_id")

            writer.writerow([name, address, lat, lng, rating, user_ratings_total, place_id])


if __name__ == "__main__":
    searcher = PlaceSearcher(API_KEY)
    print("Fetching restaurants by keywords... this may take a moment.")
    restaurants = searcher.search(LOCATION_LAT, LOCATION_LNG, RADIUS)
    print(f"Found {len(restaurants)} unique restaurants across keywords.")
    save_to_csv(restaurants, OUTPUT_CSV)
    print(f"Data saved to {OUTPUT_CSV}")
