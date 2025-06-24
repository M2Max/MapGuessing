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
KEYWORDS = ["agriturismo", "osteria", "hosteria", "trattoria", "podere", "locanda", ""]  # Keywords to include in API calls
PAUSE_BETWEEN_REQUESTS = 2.0  # Seconds pause to respect rate limits


def get_nearby_places(api_key, location, radius, place_type, keyword=None, page_token=None):
    """
    Call the Google Places Nearby Search API to get places, optionally filtered by a keyword.

    :param api_key: Your Google Maps API key
    :param location: "lat,lng" string
    :param radius: Search radius in meters
    :param place_type: Place type, e.g., 'restaurant'
    :param keyword: Optional keyword to filter places by
    :param page_token: Token for next page of results
    :return: JSON response
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": api_key,
        "location": location,
        "radius": radius,
        "type": place_type,
    }
    if keyword:
        params["keyword"] = keyword
    if page_token:
        params["pagetoken"] = page_token

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def fetch_restaurants_by_keywords(api_key, lat, lng, radius, place_type, keywords):
    """
    Retrieve restaurants for each keyword via API and deduplicate by place_id.

    :param api_key: Your Google Maps API key
    :param lat: Latitude of center point
    :param lng: Longitude of center point
    :param radius: Search radius in meters
    :param place_type: Place type, e.g., 'restaurant'
    :param keywords: List of keywords to include in API requests
    :return: List of unique places
    """
    location = f"{lat},{lng}"
    unique_places = {}

    for keyword in keywords:
        next_page_token = None
        while True:
            result = get_nearby_places(
                api_key, location, radius, place_type,
                keyword=keyword, page_token=next_page_token
            )
            for place in result.get("results", []):
                place_id = place.get("place_id")
                if place_id and place_id not in unique_places:
                    unique_places[place_id] = place
            next_page_token = result.get("next_page_token")
            if not next_page_token:
                break
            time.sleep(PAUSE_BETWEEN_REQUESTS)
        # Pause between different keyword requests as well
        time.sleep(PAUSE_BETWEEN_REQUESTS)

    return list(unique_places.values())


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
    print("Fetching restaurants by keywords... this may take a moment.")
    restaurants = fetch_restaurants_by_keywords(
        API_KEY,
        LOCATION_LAT,
        LOCATION_LNG,
        RADIUS,
        TYPE,
        KEYWORDS
    )
    print(f"Found {len(restaurants)} unique restaurants across keywords.")
    save_to_csv(restaurants, OUTPUT_CSV)
    print(f"Data saved to {OUTPUT_CSV}")
