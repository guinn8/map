import folium
from geo_utils import get_location_coordinates, get_directions_osrm, get_towns_within_diameter, sample_route_points

# List of places
places = [
    "Calgary, Alberta, Canada",  # Starting point
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

# Initialize map centered on the first location (Calgary)
m = folium.Map(location=coordinates[0], zoom_start=5)

# Plot each location on the map
for i, coord in enumerate(coordinates):
    folium.Marker(location=coord, popup=places[i].split(',')[0]).add_to(m)

# Draw routes between locations and find towns along the way
for i in range(len(coordinates) - 1):
    start_coords = coordinates[i]
    end_coords = coordinates[i + 1]
    route_data = get_directions_osrm(start_coords, end_coords)
    if route_data:
        route = route_data['routes'][0]['geometry']['coordinates']
        route = [(coord[1], coord[0]) for coord in route]  # Flip to (lat, lon)
        folium.PolyLine(route, color="blue", weight=2.5, opacity=1).add_to(m)

        # Sample points every 100 km along the route (without displaying them)
        sampled_points = sample_route_points(route, 100)
        for point in sampled_points:
            # Find and print towns within 100 km diameter around each sampled point
            towns_nearby = get_towns_within_diameter(point, 125)
            for town in towns_nearby:
                print(f"Town found: {town['name']}")
                folium.Marker(
                    location=(town['latitude'], town['longitude']),
                    popup=f"{town['name']}",
                    icon = folium.Icon(icon='info-sign', color='blue')
                ).add_to(m)

# Save the map to an HTML file
m.save("route_map_with_towns_from_calgary.html")
print("Route map saved as route_map_with_towns_from_calgary.html")
