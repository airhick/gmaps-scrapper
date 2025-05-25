import geopandas as gpd
from shapely.geometry import Polygon, Point
import numpy as np
import pandas as pd
from pyproj import Transformer
from tqdm import tqdm

# List of the 20 biggest French cities with their lat/lon (approximate)
cities = [
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Marseille", "lat": 43.2965, "lon": 5.3698},
    {"name": "Lyon", "lat": 45.7640, "lon": 4.8357},
    {"name": "Toulouse", "lat": 43.6047, "lon": 1.4442},
    {"name": "Nice", "lat": 43.7102, "lon": 7.2620},
    {"name": "Nantes", "lat": 47.2184, "lon": -1.5536},
    {"name": "Montpellier", "lat": 43.6119, "lon": 3.8777},
    {"name": "Strasbourg", "lat": 48.5734, "lon": 7.7521},
    {"name": "Bordeaux", "lat": 44.8378, "lon": -0.5792},
    {"name": "Lille", "lat": 50.6292, "lon": 3.0573},
    {"name": "Rennes", "lat": 48.1173, "lon": -1.6778},
    {"name": "Reims", "lat": 49.2583, "lon": 4.0317},
    {"name": "Le Havre", "lat": 49.4944, "lon": 0.1079},
    {"name": "Saint-Étienne", "lat": 45.4397, "lon": 4.3872},
    {"name": "Toulon", "lat": 43.1242, "lon": 5.9280},
    {"name": "Grenoble", "lat": 45.1885, "lon": 5.7245},
    {"name": "Dijon", "lat": 47.3220, "lon": 5.0415},
    {"name": "Angers", "lat": 47.4784, "lon": -0.5632},
    {"name": "Nîmes", "lat": 43.8367, "lon": 4.3601},
    {"name": "Villeurbanne", "lat": 45.7719, "lon": 4.8902},
]

# Hexagon parameters (original size)
cote_hex = 57.7  # meters
largeur_hex = 2 * cote_hex
hauteur_hex = np.sqrt(3) * cote_hex

# Area to cover around each city (radius in meters)
city_radius = 3000  # 3 km

# Transformer for WGS84 to Lambert-93
transformer = Transformer.from_crs("epsg:4326", "epsg:2154", always_xy=True)

results = []

for city in tqdm(cities, desc="Processing cities"):
    # Convert city center to Lambert-93
    city_x, city_y = transformer.transform(city["lon"], city["lat"])
    
    # Define grid bounds for the city
    xmin = city_x - city_radius
    xmax = city_x + city_radius
    ymin = city_y - city_radius
    ymax = city_y + city_radius
    
    x_range = np.arange(xmin, xmax, 1.5 * cote_hex)
    y_range = np.arange(ymin, ymax, hauteur_hex)
    
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            x_offset = 0 if j % 2 == 0 else (0.75 * largeur_hex)
            hex_center_x = x + x_offset
            hex_center_y = y
            
            # Hexagon vertices
            sommets = [
                (hex_center_x + cote_hex * np.cos(angle), hex_center_y + cote_hex * np.sin(angle))
                for angle in np.linspace(0, 2 * np.pi, 7)
            ]
            hex_poly = Polygon(sommets)
            hex_center = Point(hex_center_x, hex_center_y)
            results.append({
                "center": hex_center,
                "polygon": hex_poly,
                "city": city["name"]
            })

# Create GeoDataFrame
hex_gdf = gpd.GeoDataFrame(results, geometry='polygon', crs='EPSG:2154')

# Convert to GPS
hex_gdf = hex_gdf.to_crs(epsg=4326)

# Export CSV
csv_data = []
hexagon_counter = {}  # Counter for each city's hexagons

for idx, row in tqdm(hex_gdf.iterrows(), total=len(hex_gdf), desc="Preparing CSV data"):
    city = row["city"]
    
    # Initialize or increment counter for this city
    if city not in hexagon_counter:
        hexagon_counter[city] = 1
    else:
        hexagon_counter[city] += 1
    
    group_num = hexagon_counter[city]
    
    # Add center point
    center_lon, center_lat = row["center"].x, row["center"].y
    csv_data.append({
        "point": f"{group_num}_{city}_center",
        "coordinates": f"{center_lon},{center_lat}"
    })
    
    # Add vertices
    vertices = list(row["polygon"].exterior.coords)
    for i, (lon, lat) in enumerate(vertices[:-1]):  # Skip last point as it's same as first
        csv_data.append({
            "point": f"{group_num}_{city}_vertex{i+1}",
            "coordinates": f"{lon},{lat}"
        })

# Save to CSV
df = pd.DataFrame(csv_data)
df.to_csv("hexagones_20_villes_france_coordinates.csv", index=False)
print("CSV généré : hexagones_20_villes_france_coordinates.csv")
