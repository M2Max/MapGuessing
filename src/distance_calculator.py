import requests
import time
import csv


def calculate_distance_time(api_key, center_lat, center_lng, dest_lat, dest_lng, mode="driving"):
    """
    Calls the Google Maps Distance Matrix API to compute distance and duration.

    :param api_key: Your Google Maps API key
    :param center_lat: Latitude of the origin point
    :param center_lng: Longitude of the origin point
    :param dest_lat: Destination latitude
    :param dest_lng: Destination longitude
    :param mode: Travel mode: driving, walking, bicycling, transit
    :return: (distance_km: float, duration_text: str)
    """
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "key": api_key,
        "origins": f"{center_lat},{center_lng}",
        "destinations": f"{dest_lat},{dest_lng}",
        "mode": mode,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    element = data.get("rows", [])[0].get("elements", [])[0]
    distance_m = element.get("distance", {}).get("value")
    duration_text = element.get("duration", {}).get("text")

    distance_km = round(distance_m / 1000, 3) if distance_m is not None else None
    return distance_km, duration_text


def process_csv(input_csv, output_csv, api_key, center_lat, center_lng, mode="driving", pause=1.0):
    """
    Reads input CSV, computes distance/time for each row, and writes to output CSV.
    Expects input CSV with 'latitude' and 'longitude' columns.
    """
    with open(input_csv, newline='', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        places = list(reader)
        fieldnames = reader.fieldnames + ["distance_km", "duration_text"]

    with open(output_csv, mode='w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for place in places:
            lat = place.get("latitude")
            lng = place.get("longitude")
            if not lat or not lng:
                place["distance_km"] = None
                place["duration_text"] = None
            else:
                dist_km, dur_text = calculate_distance_time(
                    api_key, center_lat, center_lng, lat, lng, mode
                )
                place["distance_km"] = dist_km
                place["duration_text"] = dur_text
                time.sleep(pause)

            writer.writerow(place)


def main():
    # Hardcoded configuration
    api_key = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace
    input_csv = "restaurants_nearby.csv"
    output_csv = "distances_output.csv"
    center_lat = 1234  # Example: New York City
    center_lng = 1234
    mode = "driving"
    pause = 1.0

    process_csv(
        input_csv,
        output_csv,
        api_key,
        center_lat,
        center_lng,
        mode,
        pause
    )
    print(f"Results written to {output_csv}")


if __name__ == "__main__":
    main()
