import geopandas as gpd
from shapely.geometry import Polygon, Point
import numpy as np
import pandas as pd
from pyproj import Transformer
from tqdm import tqdm

# Saisie utilisateur pour la taille du côté
while True:
    try:
        cote_hex = float(input("Entrez la longueur des côtés des hexagones en mètres (ex: 57.7): "))
        if cote_hex <= 0:
            print("La longueur doit être positive.")
            continue
        break
    except ValueError:
        print("Veuillez entrer un nombre valide.")

# Rayon de la zone à couvrir autour de chaque ville (fixe)
city_radius = 3000  # 3 km
print(f"\nPour une longueur de côté de {cote_hex}m, la zone couverte autour de chaque ville sera un cercle de {city_radius}m de rayon.")

# Liste des 20 plus grandes villes de France
cities = [
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522, "area": 17174},
    {"name": "Marseille", "lat": 43.2965, "lon": 5.3698, "area": 3173},
    {"name": "Lyon", "lat": 45.7640, "lon": 4.8357, "area": 3287},
    {"name": "Toulouse", "lat": 43.6047, "lon": 1.4442, "area": 2538},
    {"name": "Nice", "lat": 43.7102, "lon": 7.2620, "area": 1479},
    {"name": "Nantes", "lat": 47.2184, "lon": -1.5536, "area": 1157},
    {"name": "Montpellier", "lat": 43.6119, "lon": 3.8777, "area": 1005},
    {"name": "Strasbourg", "lat": 48.5734, "lon": 7.7521, "area": 1157},
    {"name": "Bordeaux", "lat": 44.8378, "lon": -0.5792, "area": 2287},
    {"name": "Lille", "lat": 50.6292, "lon": 3.0573, "area": 1666},
    {"name": "Rennes", "lat": 48.1173, "lon": -1.6778, "area": 1189},
    {"name": "Reims", "lat": 49.2583, "lon": 4.0317, "area": 946},
    {"name": "Le Havre", "lat": 49.4944, "lon": 0.1079, "area": 1190},
    {"name": "Saint-Étienne", "lat": 45.4397, "lon": 4.3872, "area": 943},
    {"name": "Toulon", "lat": 43.1242, "lon": 5.9280, "area": 1036},
    {"name": "Grenoble", "lat": 45.1885, "lon": 5.7245, "area": 1021},
    {"name": "Dijon", "lat": 47.3220, "lon": 5.0415, "area": 1043},
    {"name": "Angers", "lat": 47.4784, "lon": -0.5632, "area": 1003},
    {"name": "Nîmes", "lat": 43.8367, "lon": 4.3601, "area": 1013},
]

# Paramètres de l'hexagone
largeur_hex = 2 * cote_hex
hauteur_hex = np.sqrt(3) * cote_hex

# Transformer pour WGS84 -> Lambert-93
transformer = Transformer.from_crs("epsg:4326", "epsg:2154", always_xy=True)
reverse_transformer = Transformer.from_crs("epsg:2154", "epsg:4326", always_xy=True)

results = []

for city in tqdm(cities, desc="Processing cities"):
    # Calculer le rayon à partir de la superficie (en km²), puis réduire par 10
    area_km2 = city["area"]
    city_radius = np.sqrt(area_km2 / np.pi) * 1000 * 0.1  # en mètres (réduit par 10)
    print(f"{city['name']} : aire urbaine {area_km2} km², rayon utilisé {city_radius:.1f} m")
    # Centre-ville en Lambert-93
    city_x, city_y = transformer.transform(city["lon"], city["lat"])
    
    # Définir les bornes du carré englobant le cercle de city_radius
    xmin = city_x - city_radius
    xmax = city_x + city_radius
    ymin = city_y - city_radius
    ymax = city_y + city_radius
    
    # Générer la grille pointy-topped (pointe en haut)
    x_range = np.arange(xmin, xmax, 1.5 * cote_hex)
    y_range = np.arange(ymin, ymax, hauteur_hex)
    
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            # Décaler chaque colonne impaire de la moitié de la hauteur d'un hexagone
            y_offset = (hauteur_hex / 2) if i % 2 else 0
            hex_center_x = x
            hex_center_y = y + y_offset
            
            # Vérifier si le centre de l'hexagone est dans le cercle de city_radius
            if np.sqrt((hex_center_x - city_x) ** 2 + (hex_center_y - city_y) ** 2) > city_radius:
                continue
            
            # Sommets de l'hexagone
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

# Création du GeoDataFrame
hex_gdf = gpd.GeoDataFrame(results, geometry='polygon', crs='EPSG:2154')

# Conversion en GPS
hex_gdf = hex_gdf.to_crs(epsg=4326)

# Export CSV
csv_data = []
hexagon_counter = {}

for idx, row in tqdm(hex_gdf.iterrows(), total=len(hex_gdf), desc="Preparing CSV data"):
    city = row["city"]
    
    # Compteur d'hexagones par ville
    if city not in hexagon_counter:
        hexagon_counter[city] = 1
    else:
        hexagon_counter[city] += 1
    group_num = hexagon_counter[city]
    
    # Centre
    center_lon, center_lat = row["center"].x, row["center"].y
    csv_data.append({
        "point": f"{group_num}_{city}_center",
        "coordinates": f"{center_lon},{center_lat}"
    })
    
    # Sommets
    vertices = list(row["polygon"].exterior.coords)
    for i, (lon, lat) in enumerate(vertices[:-1]):  # On saute le dernier car il est identique au premier
        csv_data.append({
            "point": f"{group_num}_{city}_vertex{i+1}",
            "coordinates": f"{lon},{lat}"
        })

# Sauvegarde CSV
df = pd.DataFrame(csv_data)
df.to_csv("hexagones_20_villes_france_coordinates.csv", index=False)
print("CSV généré : hexagones_20_villes_france_coordinates.csv") 