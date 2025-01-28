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
    Create an interactive map from OSM data with points from database and administrative boundaries
    """
    # Load the data
    graph = ox.graph_from_xml(osm_file_path)
    nodes, edges = ox.graph_to_gdfs(graph)
    
    # Load additional features
    buildings = ox.features_from_xml(osm_file_path, tags={'building': True})
    green_areas = ox.features_from_xml(osm_file_path, tags={'landuse': ['grass', 'park', 'forest']})
    water_bodies = ox.features_from_xml(osm_file_path, tags={'natural': 'water'})
    
    # Load administrative boundaries
    districts = ox.features_from_xml(osm_file_path, tags={
        'admin_level': '9',  # Districts in Cologne
        'boundary': 'administrative'
    })
    boroughs = ox.features_from_xml(osm_file_path, tags={
        'admin_level': '6',  # Boroughs in Cologne
        'boundary': 'administrative'
    })
    
    # Ensure all data is in WGS84 (EPSG:4326)
    edges = edges.to_crs(epsg=4326)
    buildings = buildings.to_crs(epsg=4326)
    green_areas = green_areas.to_crs(epsg=4326)
    water_bodies = water_bodies.to_crs(epsg=4326)
    districts = districts.to_crs(epsg=4326)
    boroughs = boroughs.to_crs(epsg=4326)
    
    # Create base map
    m = folium.Map(
        location=[50.9333, 6.9500],  # Cologne's coordinates
        zoom_start=12,
        prefer_canvas=True,
        min_zoom=10,
        max_zoom=18
    )
    
    # Add custom CSS and JavaScript for fullscreen functionality
    custom_css = """
        <style>
            .fullscreen-overlay {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.9);
                z-index: 9999;
                justify-content: center;
                align-items: center;
                cursor: pointer;
            }
            .fullscreen-image {
                max-width: 90%;
                max-height: 90%;
                object-fit: contain;
            }
            .popup-image {
                cursor: pointer;
                transition: transform 0.2s;
            }
            .popup-image:hover {
                transform: scale(1.05);
            }
            .close-button {
                position: fixed;
                top: 20px;
                right: 20px;
                color: white;
                font-size: 30px;
                cursor: pointer;
                background: none;
                border: none;
                padding: 10px;
            }
        </style>
    """
    
    custom_js = """
        <script>
        function showFullscreen(imgSrc) {
            // Create overlay if it doesn't exist
            if (!document.getElementById('fullscreen-overlay')) {
                const overlay = document.createElement('div');
                overlay.id = 'fullscreen-overlay';
                overlay.className = 'fullscreen-overlay';
                
                const closeBtn = document.createElement('button');
                closeBtn.className = 'close-button';
                closeBtn.innerHTML = '×';
                closeBtn.onclick = hideFullscreen;
                
                const img = document.createElement('img');
                img.className = 'fullscreen-image';
                
                overlay.appendChild(closeBtn);
                overlay.appendChild(img);
                document.body.appendChild(overlay);
                
                overlay.onclick = function(e) {
                    if (e.target === overlay) {
                        hideFullscreen();
                    }
                };
            }
            
            // Update and show overlay
            const overlay = document.getElementById('fullscreen-overlay');
            const fullscreenImg = overlay.querySelector('.fullscreen-image');
            fullscreenImg.src = imgSrc;
            overlay.style.display = 'flex';
        }
        
        function hideFullscreen() {
            const overlay = document.getElementById('fullscreen-overlay');
            if (overlay) {
                overlay.style.display = 'none';
            }
        }
        </script>
    """
    
    # Add custom CSS and JavaScript to the map
    m.get_root().header.add_child(folium.Element(custom_css))
    m.get_root().header.add_child(folium.Element(custom_js))
    
    # Add district boundaries
    if not districts.empty:
        folium.GeoJson(
            districts,
            name='Districts',
            style_function=lambda x: {
                'fillColor': '#ffcdd2',
                'color': '#e57373',
                'weight': 2,
                'fillOpacity': 0.1,
                'dashArray': '5, 5'
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['name'],
                aliases=['District'],
                style=('background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;')
            )
        ).add_to(m)
    
    # Add borough boundaries
    if not boroughs.empty:
        borough_layer = folium.GeoJson(
            boroughs,
            name='Boroughs',
            style_function=lambda x: {
                'fillColor': '#c5cae9',
                'color': '#7986cb',
                'weight': 1,
                'fillOpacity': 0.1,
                'dashArray': '3, 3'
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['name'],
                aliases=['Borough'],
                style=('background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;')
            )
        ).add_to(m)
    
    # Add all the map layers (buildings, green areas, water bodies)
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
        
        # Create HTML for popup with clickable image
        img_html = f'''
            <img src="{image_path}" 
                 class="popup-image" 
                 style="width:200px;" 
                 onclick="showFullscreen('{image_path}')"
                 title="Click to view fullscreen">
        '''
        
        popup_html = f'''
            <div style="width:220px;">
                {img_html}<br>
                <p>{description}</p>
            </div>
        '''
        
        # Add marker with popup
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color='red',
            fill=True,
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def main():
    setup_database()
        
    # Create and save the map
    map_obj = create_interactive_map('/home/thea/Dokumente/github/where-is-sony/cologne_shapefiles/bayenthal.osm')
    map_obj.save('cologne_interactive.html')

if __name__ == "__main__":
    main()