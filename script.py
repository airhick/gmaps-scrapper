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

# Rayon fixe de 5km pour Genève
city_radius = 5000  # 5 km
print(f"\nPour une longueur de côté de {cote_hex}m, la zone couverte autour de Genève sera un cercle de {city_radius}m de rayon.")

# Liste contenant uniquement Genève
cities = [
    {"name": "Geneve", "lat": 46.2044, "lon": 6.1432},
]

# Paramètres de l'hexagone
largeur_hex = 2 * cote_hex
hauteur_hex = np.sqrt(3) * cote_hex

# Transformer pour WGS84 -> CH1903+ (système de coordonnées suisse)
transformer = Transformer.from_crs("epsg:4326", "epsg:2056", always_xy=True)
reverse_transformer = Transformer.from_crs("epsg:2056", "epsg:4326", always_xy=True)

results = []

for city in tqdm(cities, desc="Processing Geneva"):
    print(f"{city['name']} : rayon utilisé {city_radius:.1f} m")
    # Centre-ville en CH1903+
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
hex_gdf = gpd.GeoDataFrame(results, geometry='polygon', crs='EPSG:2056')

# Conversion en GPS
hex_gdf = hex_gdf.to_crs(epsg=4326)

# Export CSV
csv_data = []
hexagon_counter = {}
seen_coordinates = set() # Pour suivre les coordonnées déjà vues

for idx, row in tqdm(hex_gdf.iterrows(), total=len(hex_gdf), desc="Préparation des données CSV"):
    city = row["city"]
    
    # Compteur d'hexagones par ville
    if city not in hexagon_counter:
        hexagon_counter[city] = 1
    else:
        hexagon_counter[city] += 1
    group_num = hexagon_counter[city]
    
    # Centre (calculé à partir du centroïde du polygone reprojeté)
    centroid = row["polygon"].centroid
    center_lon, center_lat = centroid.x, centroid.y
    # Arrondir les coordonnées à 6 décimales (environ 11 cm de précision)
    center_lon = round(center_lon, 6)
    center_lat = round(center_lat, 6)
    center_coords = f"{center_lon},{center_lat}"
    
    if center_coords not in seen_coordinates:
        seen_coordinates.add(center_coords)
        csv_data.append({
            "point": f"{group_num}_{city}_center",
            "coordinates": center_coords
        })
    
    # Sommets
    vertices = list(row["polygon"].exterior.coords)
    for i, (lon, lat) in enumerate(vertices[:-1]): # On saute le dernier car il est identique au premier
        # Arrondir les coordonnées à 6 décimales
        lon = round(lon, 6)
        lat = round(lat, 6)
        vertex_coords = f"{lon},{lat}"
        
        if vertex_coords not in seen_coordinates:
            seen_coordinates.add(vertex_coords)
            csv_data.append({
                "point": f"{group_num}_{city}_vertex{i+1}",
                "coordinates": vertex_coords
            })

# Sauvegarde CSV
df = pd.DataFrame(csv_data)
output_file = "hexagones_geneve_5km_coordinates.csv"
df.to_csv(output_file, index=False)
print(f"CSV généré : {output_file}")
print(f"Nombre total de points uniques : {len(csv_data)}") 