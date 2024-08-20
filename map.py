import requests
import folium

# Function to get coordinates from OpenStreetMap Nominatim
def get_location_coordinates(place_name):
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

# Function to get driving directions using OSRM
def get_directions_osrm(start_coords, end_coords):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=geojson"
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching route from {start_coords} to {end_coords}: {e}")
        return None

# List of places
places = [
    "Paul Lake Provincial Park, British Columbia, Canada",
    "Beaumont Provincial Park, British Columbia, Canada",
    "Meziadin Lake Provincial Park, British Columbia, Canada",
    "Boya Lake Provincial Park, British Columbia, Canada",
    "Robert Service Campground, Whitehorse, Yukon, Canada",
    "Kathleen Lake, Yukon, Canada"
]

# Get coordinates for all locations
coordinates = [get_location_coordinates(place) for place in places]

# Filter out any None values in coordinates
coordinates = [coord for coord in coordinates if coord is not None]

if not coordinates:
    print("Error: No valid coordinates found. Exiting.")
    exit(1)

# Initialize map centered on the first location
m = folium.Map(location=coordinates[0], zoom_start=5)

# Plot each location on the map
for i, coord in enumerate(coordinates):
    folium.Marker(location=coord, popup=places[i].split(',')[0]).add_to(m)

# Draw routes between locations
for i in range(len(coordinates) - 1):
    start_coords = coordinates[i]
    end_coords = coordinates[i + 1]
    route_data = get_directions_osrm(start_coords, end_coords)
    if route_data:
        route = route_data['routes'][0]['geometry']['coordinates']
        route = [(coord[1], coord[0]) for coord in route]  # Flip to (lat, lon)
        folium.PolyLine(route, color="blue", weight=2.5, opacity=1).add_to(m)

# Save the map to an HTML file
m.save("route_map.html")
print("Route map saved as route_map.html")

