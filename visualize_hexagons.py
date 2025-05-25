import folium
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import ast

def create_map():
    # Read the CSV file
    df = pd.read_csv('hexagones_20_villes_france_coordinates.csv')
    
    # Create a base map centered on France
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
    
    # Group the data by the point identifier (to group hexagon points together)
    current_group = None
    hex_coords = []
    
    # Process each row
    for _, row in df.iterrows():
        point_id = row['point']
        coords = row['coordinates'].split(',')
        lon, lat = float(coords[0]), float(coords[1])
        
        # Extract group number and city from point_id
        parts = point_id.split('_')
        group_num = parts[0]
        city = parts[1]
        
        # If we're starting a new group
        if current_group != group_num:
            # If we have a complete hexagon, add it to the map
            if len(hex_coords) == 7:  # 6 vertices + center
                # Create polygon
                hex_poly = folium.Polygon(
                    locations=hex_coords[:-1],  # Exclude center point
                    color='blue',
                    weight=1,
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.2,
                    popup=f'City: {city}<br>Group: {group_num}'
                )
                hex_poly.add_to(m)
                
                # Add center point
                folium.CircleMarker(
                    location=hex_coords[-1],
                    radius=3,
                    color='red',
                    fill=True,
                    popup=f'Center - City: {city}<br>Group: {group_num}'
                ).add_to(m)
            
            # Start new group
            current_group = group_num
            hex_coords = []
        
        # Add coordinates to current hexagon
        hex_coords.append([lat, lon])
    
    # Add the last hexagon if it exists
    if len(hex_coords) == 7:
        hex_poly = folium.Polygon(
            locations=hex_coords[:-1],
            color='blue',
            weight=1,
            fill=True,
            fill_color='blue',
            fill_opacity=0.2,
            popup=f'City: {city}<br>Group: {group_num}'
        )
        hex_poly.add_to(m)
        
        folium.CircleMarker(
            location=hex_coords[-1],
            radius=3,
            color='red',
            fill=True,
            popup=f'Center - City: {city}<br>Group: {group_num}'
        ).add_to(m)
    
    # Add a layer control
    folium.LayerControl().add_to(m)
    
    # Save the map
    m.save('france_hexagons_map.html')
    print("Map generated: france_hexagons_map.html")

if __name__ == "__main__":
    create_map() 