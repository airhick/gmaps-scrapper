import folium
import pandas as pd
import json
from folium.plugins import MarkerCluster
import webbrowser
import os

def create_hexagon_map(csv_file):
    print(f"Lecture du fichier CSV : {csv_file}")
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file)
        print(f"Nombre de lignes dans le CSV : {len(df)}")
        print("Aperçu des données :")
        print(df.head())
    except Exception as e:
        print(f"Erreur lors de la lecture du CSV : {str(e)}")
        return
    
    # Create a map centered on France
    france_center = [46.603354, 1.888334]  # Center of France
    m = folium.Map(location=france_center, zoom_start=6)
    
    # Create a marker cluster for better performance
    marker_cluster = MarkerCluster().add_to(m)
    
    # Group the data by city
    cities = df['point'].str.split('_').str[1].unique()
    print(f"\nVilles trouvées : {len(cities)}")
    print(cities)
    
    # Define colors for different cities
    colors = [
        'red', 'blue', 'green', 'purple', 'orange', 'darkred',
        'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
        'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray',
        'black', 'lightgray', 'darkorange', 'lightpurple'
    ]
    
    hexagon_count = 0
    # Process each city
    for city_idx, city in enumerate(cities):
        city_data = df[df['point'].str.contains(city)]
        color = colors[city_idx % len(colors)]
        
        # Group by hexagon number
        hex_groups = city_data['point'].str.split('_').str[0].unique()
        print(f"\nTraitement de {city} : {len(hex_groups)} hexagones trouvés")
        
        for hex_num in hex_groups:
            hex_data = city_data[city_data['point'].str.startswith(f"{hex_num}_{city}")]
            
            try:
                # Get center coordinates
                center_coords = hex_data[hex_data['point'].str.contains('center')]['coordinates'].iloc[0]
                center_lon, center_lat = map(float, center_coords.split(','))
                
                # Get vertices coordinates
                vertices = hex_data[hex_data['point'].str.contains('vertex')]['coordinates'].tolist()
                # Inverser chaque paire pour Folium : [lat, lon]
                vertices_coords = [[float(coord.split(',')[1]), float(coord.split(',')[0])] for coord in vertices]
                
                # Create hexagon polygon
                folium.Polygon(
                    locations=vertices_coords,
                    color=color,
                    weight=2,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.2,
                    popup=f"{city} - Hexagon {hex_num}"
                ).add_to(m)
                
                # Add center marker (inverser aussi)
                folium.CircleMarker(
                    location=[center_lat, center_lon],
                    radius=3,
                    color=color,
                    fill=True,
                    popup=f"{city} - Center {hex_num}"
                ).add_to(marker_cluster)
                
                hexagon_count += 1
            except Exception as e:
                print(f"Erreur lors du traitement de l'hexagone {hex_num} de {city} : {str(e)}")
    
    print(f"\nNombre total d'hexagones créés : {hexagon_count}")
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save the map
    output_file = 'france_hexagons_map.html'
    try:
        m.save(output_file)
        print(f"\nCarte sauvegardée dans : {os.path.abspath(output_file)}")
        
        # Open the map in the default web browser
        file_path = 'file://' + os.path.realpath(output_file)
        print(f"Tentative d'ouverture de : {file_path}")
        webbrowser.open(file_path)
        
        print("\nSi la carte ne s'ouvre pas automatiquement, vous pouvez l'ouvrir manuellement en ouvrant le fichier :")
        print(os.path.abspath(output_file))
    except Exception as e:
        print(f"Erreur lors de la sauvegarde ou de l'ouverture de la carte : {str(e)}")

if __name__ == "__main__":
    csv_file = "hexagones_20_villes_france_coordinates.csv"
    if os.path.exists(csv_file):
        print(f"Fichier CSV trouvé : {os.path.abspath(csv_file)}")
        create_hexagon_map(csv_file)
    else:
        print(f"Erreur : Le fichier {csv_file} n'existe pas dans le répertoire : {os.getcwd()}")
        print("Veuillez d'abord exécuter script.py pour générer les données.") 