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
    
    # Create a map centered on Geneva
    geneva_center = [46.2044, 6.1432]  # Center of Geneva
    m = folium.Map(location=geneva_center, zoom_start=13)  # Revert zoom to 13 for city view
    
    # Create a marker cluster for better performance
    marker_cluster = MarkerCluster().add_to(m)
    
    # Define color for Geneva
    color = 'red'
    
    # Plot each point
    for _, row in df.iterrows():
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
    output_file = 'geneve_5km_hexagons_map.html' # Updated HTML output filename
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
    csv_file = "hexagones_geneve_5km_coordinates.csv"  # Updated filename
    if os.path.exists(csv_file):
        print(f"Fichier CSV trouvé : {os.path.abspath(csv_file)}")
        create_hexagon_map(csv_file)
    else:
        print(f"Erreur : Le fichier {csv_file} n'existe pas dans le répertoire : {os.getcwd()}")
        print("Veuillez d'abord exécuter script.py pour générer les données.") 