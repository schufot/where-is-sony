import osmnx as ox
import folium
from folium import plugins
import geopandas as gpd
import sqlite3
import base64
from pathlib import Path
import os

# Database setup
def setup_database():
    """Create SQLite database and necessary tables"""
    conn = sqlite3.connect('map_points.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            description TEXT NOT NULL,
            image_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_point(latitude, longitude, description, image_path):
    """Add a new point to the database"""
    conn = sqlite3.connect('map_points.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO points (latitude, longitude, description, image_path)
        VALUES (?, ?, ?, ?)
    ''', (latitude, longitude, description, image_path))
    
    conn.commit()
    conn.close()

def get_all_points():
    """Retrieve all points from the database"""
    conn = sqlite3.connect('map_points.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM points')
    points = c.fetchall()
    
    conn.close()
    return points

def create_interactive_map(osm_file_path):
    """
    Create an interactive map from OSM data with points from database
    """
    # Load the data
    graph = ox.graph_from_xml(osm_file_path)
    nodes, edges = ox.graph_to_gdfs(graph)
    
    # Load additional features
    buildings = ox.features_from_xml(osm_file_path, tags={'building': True})
    green_areas = ox.features_from_xml(osm_file_path, tags={'landuse': ['grass', 'park', 'forest']})
    water_bodies = ox.features_from_xml(osm_file_path, tags={'natural': 'water'})
    
    # Ensure all data is in WGS84 (EPSG:4326)
    edges = edges.to_crs(epsg=4326)
    buildings = buildings.to_crs(epsg=4326)
    green_areas = green_areas.to_crs(epsg=4326)
    water_bodies = water_bodies.to_crs(epsg=4326)
    
    # Calculate center point for initial map view
    center_lat = edges.unary_union.centroid.y
    center_lon = edges.unary_union.centroid.x
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15,
        prefer_canvas=True
    )
    
    # Add buildings
    if not buildings.empty:
        folium.GeoJson(
            buildings,
            name='Buildings',
            style_function=lambda x: {
                'fillColor': '#d9d0c9',
                'color': '#beb7ae',
                'weight': 1,
                'fillOpacity': 0.7
            },
            show=False
        ).add_to(m)
    
    # Add green areas
    if not green_areas.empty:
        folium.GeoJson(
            green_areas,
            name='Green Areas',
            style_function=lambda x: {
                'fillColor': '#add19e',
                'color': '#8fc07f',
                'weight': 1,
                'fillOpacity': 0.7
            }
        ).add_to(m)
    
    # Add water bodies
    if not water_bodies.empty:
        folium.GeoJson(
            water_bodies,
            name='Water',
            style_function=lambda x: {
                'fillColor': '#aad3df',
                'color': '#7ab6d6',
                'weight': 1,
                'fillOpacity': 0.7
            }
        ).add_to(m)
    
   
    # Add points from database with popups
    points = get_all_points()
    for point in points:
        id, lat, lon, description, image_path, created_at = point
        
        # Create HTML for popup
        img_html = f'<img src="{image_path}" style="width:200px;"><br>'
        popup_html = f'''
            <div style="width:220px;">
                {img_html}
                <p>{description}</p>
            </div>
        '''
        
        # Add marker with popup
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def main():
    # Setup database if it doesn't exist
    setup_database()
    
    # Example of adding a point (you would typically do this separately)
    # add_point(50.9333, 6.9500, "Test point in Cologne", "path/to/image.jpg")
    
    # Create and save the map
    map_obj = create_interactive_map('/home/thea/Dokumente/GitHub/where-is-sony/cologne_shapefiles/bayenthal.osm')
    map_obj.save('cologne_interactive.html')

if __name__ == "__main__":
    main()