import requests
from geopy.distance import geodesic

def get_location_coordinates(place_name):
    """Fetches coordinates (latitude, longitude) for a given place using Nominatim API."""
    try:
        headers = {
            'User-Agent': 'MyApp (your_email@example.com)'  # Replace with your email or other identification
        }
        url = f"https://nominatim.openstreetmap.org/search?q={place_name}&format=json"
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            print(f"Warning: No data found for {place_name}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {place_name}: {e}")
        return None

def get_directions_osrm(start_coords, end_coords):
    """Fetches driving directions between two points using the OSRM API."""
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=geojson"
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching route from {start_coords} to {end_coords}: {e}")
        return None

def calculate_bounding_box(center_coords, diameter_km):
    """Calculates a bounding box around a central point for a given diameter (in km)."""
    half_side = diameter_km / 2 / 111  # Approx 111 km per degree of latitude
    lat, lon = center_coords
    return [lat - half_side, lon - half_side, lat + half_side, lon + half_side]

def get_towns_within_diameter(center_coords, diameter_km):
    """Finds towns and cities within a specified diameter around a central point using Overpass API."""
    bounding_box = calculate_bounding_box(center_coords, diameter_km)
    bbox_str = f"{bounding_box[0]},{bounding_box[1]},{bounding_box[2]},{bounding_box[3]}"

    query = f"""
    [out:json];
    (
      node["place"="town"]({bbox_str});
      node["place"="city"]({bbox_str});
    );
    out body;
    """
    url = "http://overpass-api.de/api/interpreter"
    response = requests.post(url, data={'data': query})
    response.raise_for_status()
    data = response.json()

    towns_and_cities_within_diameter = []
    for element in data['elements']:
        town_city_coords = (element['lat'], element['lon'])
        distance = geodesic(center_coords, town_city_coords).kilometers
        if distance <= diameter_km / 2:
            towns_and_cities_within_diameter.append({
                "name": element['tags'].get('name', 'Unknown'),
                "latitude": element['lat'],
                "longitude": element['lon'],
                "distance_km": distance
            })

    return towns_and_cities_within_diameter

def calculate_distance(coord1, coord2):
    """Calculates the distance between two coordinates."""
    return geodesic(coord1, coord2).kilometers

def sample_route_points(route_coords, interval_km):
    """Samples points along a route every specified interval in kilometers."""
    sampled_points = []
    accumulated_distance = 0
    for i in range(1, len(route_coords)):
        segment_distance = calculate_distance(route_coords[i - 1], route_coords[i])
        accumulated_distance += segment_distance
        if accumulated_distance >= interval_km:
            sampled_points.append(route_coords[i])
            accumulated_distance = 0  # Reset distance counter
    return sampled_points
