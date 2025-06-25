import csv

# Hardcoded configuration
INPUT_CSV = "distances_output.csv"  # Output from previous script
MIN_DISTANCE_KM = 11.5
MAX_DISTANCE_KM = 12.5
MIN_DURATION_MIN = 15
MAX_DURATION_MIN = 25


class PlaceFilter:
    def __init__(self, min_distance_km, max_distance_km, min_duration_min, max_duration_min):
        self.min_distance_km = min_distance_km
        self.max_distance_km = max_distance_km
        self.min_duration_min = min_duration_min
        self.max_duration_min = max_duration_min

    @staticmethod
    def parse_duration(duration_text):
        """
        Convert a duration string like '18 mins' or '1 hour 5 mins' to total minutes (int).
        """
        parts = duration_text.split()
        total = 0
        i = 0
        while i < len(parts):
            try:
                value = int(parts[i])
                unit = parts[i+1]
                if unit.startswith('hour'):
                    total += value * 60
                elif unit.startswith('min'):
                    total += value
                i += 2
            except (ValueError, IndexError):
                i += 1
        return total

    def filter(self, places):
        """
        Filter places by distance and duration.
        """
        matches = []
        for row in places:
            try:
                dist = float(row.get('distance_km', 0))
            except ValueError:
                continue
            dur_text = row.get('duration_text', '')
            duration_min = self.parse_duration(dur_text)

            if (self.min_distance_km <= dist <= self.max_distance_km and
                self.min_duration_min <= duration_min <= self.max_duration_min):
                matches.append({
                    'name': row.get('name'),
                    'address': row.get('address'),
                    'latitude': row.get('latitude'),
                    'longitude': row.get('longitude'),
                    'place_id': row.get('place_id'),
                    'rating': row.get('rating'),
                    'distance_km': dist,
                    'duration_text': dur_text
                })
        return matches


def filter_places(input_csv):
    """
    Reads the input CSV, filters places by distance and duration, returns matching rows.
    """
    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        places = [row for row in reader]
    
    place_filter = PlaceFilter(MIN_DISTANCE_KM, MAX_DISTANCE_KM, MIN_DURATION_MIN, MAX_DURATION_MIN)
    return place_filter.filter(places)


def main():
    results = filter_places(INPUT_CSV)
    if not results:
        print("No places found within the specified distance and duration ranges.")
    else:
        print(f"Found {len(results)} matching places:")
        for place in results:
            print(f"- {place['name']} | {place['address']} | {place['distance_km']} km | {place['duration_text']}")

if __name__ == '__main__':
    main()
