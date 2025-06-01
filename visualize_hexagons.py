import folium
import pandas as pd
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
    
    # Define colors for different cities
    colors = [
        'red', 'blue', 'green', 'purple', 'orange', 'darkred',
        'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
        'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray',
        'black', 'lightgray', 'darkorange', 'lightpurple'
    ]
    
    # Group points by city
    df['city'] = df['point'].str.split('_').str[1]
    
    # Plot each point
    for city_idx, city in enumerate(df['city'].unique()):
        city_data = df[df['city'] == city]
        color = colors[city_idx % len(colors)]
        for _, row in city_data.iterrows():
            lon, lat = map(float, row['coordinates'].split(','))
            folium.CircleMarker(
                location=[lat, lon],
                radius=3,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=f"{row['point']}<br>({lat}, {lon})"
            ).add_to(marker_cluster)
    
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