import folium
import pandas as pd
from folium.plugins import MarkerCluster
import branca.colormap as cm

def create_map():
    # Read the CSV file
    print("Reading CSV file...")
    df = pd.read_csv('hexagones_20_villes_france_coordinates.csv')
    
    # Create a base map centered on France
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
    
    # Create a color map for cities
    cities = df['point'].str.split('_').str[1].unique()
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 
              'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray', 'darkred', 'darkblue']
    city_colors = dict(zip(cities, colors))
    
    # Create feature groups for each city
    city_groups = {}
    for city in cities:
        city_groups[city] = folium.FeatureGroup(name=city)
    
    print("Processing hexagons...")
    # Group the data by the point identifier
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
                    color=city_colors[city],
                    weight=1,
                    fill=True,
                    fill_color=city_colors[city],
                    fill_opacity=0.2,
                    popup=f'City: {city}<br>Group: {group_num}'
                )
                hex_poly.add_to(city_groups[city])
                
                # Add center point
                folium.CircleMarker(
                    location=hex_coords[-1],
                    radius=2,
                    color=city_colors[city],
                    fill=True,
                    popup=f'Center - City: {city}<br>Group: {group_num}'
                ).add_to(city_groups[city])
            
            # Start new group
            current_group = group_num
            hex_coords = []
        
        # Add coordinates to current hexagon
        hex_coords.append([lat, lon])
    
    # Add the last hexagon if it exists
    if len(hex_coords) == 7:
        hex_poly = folium.Polygon(
            locations=hex_coords[:-1],
            color=city_colors[city],
            weight=1,
            fill=True,
            fill_color=city_colors[city],
            fill_opacity=0.2,
            popup=f'City: {city}<br>Group: {group_num}'
        )
        hex_poly.add_to(city_groups[city])
        
        folium.CircleMarker(
            location=hex_coords[-1],
            radius=2,
            color=city_colors[city],
            fill=True,
            popup=f'Center - City: {city}<br>Group: {group_num}'
        ).add_to(city_groups[city])
    
    # Add all city groups to the map
    for city_group in city_groups.values():
        city_group.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add minimap
    minimap = folium.plugins.MiniMap()
    m.add_child(minimap)
    
    # Add fullscreen option
    folium.plugins.Fullscreen().add_to(m)
    
    print("Saving map...")
    # Save the map
    m.save('france_hexagons_map.html')
    print("Map generated: france_hexagons_map.html")

if __name__ == "__main__":
    create_map() 