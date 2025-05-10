import osmnx as ox
import folium
from folium import plugins
import geopandas as gpd
import sqlite3
import base64
from pathlib import Path
import os
from shapely.geometry import box, Polygon
import json

def convert_esri_geojson_to_polygon(filepath):
    """
    Converts an ESRI-style GeoJSON with 'rings' into a standard GeoDataFrame
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check if the expected structure exists
        if not data.get("features") or len(data["features"]) == 0:
            print(f"ERROR: GeoJSON file {filepath} has no features")
            raise ValueError("Invalid GeoJSON: No features found")
            
        # Take the first feature's ring as the main polygon
        rings = data["features"][0]["geometry"].get("rings")
        if not rings or len(rings) == 0:
            print(f"ERROR: GeoJSON feature has no rings at {filepath}")
            raise ValueError("Invalid GeoJSON: No rings found in feature")
            
        # ESRI GeoJSON typically has longitude,latitude ordering
        try:
            polygon = Polygon(rings[0])
            
            # Create a GeoDataFrame with EPSG:4326
            gdf = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")
            bounds = gdf.total_bounds
            # Print bounds correctly labeled [west, south, east, north]
            print(f"Successfully loaded boundary with bounds [west, south, east, north]: [{bounds[0]}, {bounds[1]}, {bounds[2]}, {bounds[3]}]")
            return gdf
        except Exception as e:
            print(f"ERROR creating polygon: {e}")
            raise
            
    except json.JSONDecodeError:
        print(f"ERROR: {filepath} is not valid JSON")
        raise
    except Exception as e:
        print(f"ERROR loading GeoJSON file {filepath}: {e}")
        raise

def create_interactive_map(osm_file_path, boundary_geojson_path):
    """
    Create an interactive folium map showing only Cologne, masking the rest of the world.
    """
    # Load and convert the ESRI-style GeoJSON
    boundary = convert_esri_geojson_to_polygon(boundary_geojson_path)

    # Create a bounding box of the world
    world = gpd.GeoDataFrame(geometry=[box(-180, -90, 180, 90)], crs="EPSG:4326")

    # Create a mask: World minus Cologne
    mask = gpd.overlay(world, boundary, how="difference")

    # Load OSM data and extract edges (optional for background)
    graph = ox.graph_from_xml(osm_file_path)
    nodes, edges = ox.graph_to_gdfs(graph)
    edges = edges.to_crs(epsg=4326)

    # Center the map on Cologne
    cologne_center = [50.9333, 6.9500]
    m = folium.Map(location=cologne_center, zoom_start=13, min_zoom=12, max_bounds=True)

    # Set map bounds to the Cologne boundary
    south, west, north, east = boundary.total_bounds
    m.fit_bounds([[south, west], [north, east]])
    m.options['maxBounds'] = [[south, west], [north, east]]

    # Add the gray mask outside Cologne
    folium.GeoJson(
        mask,
        name="Outside Cologne",
        style_function=lambda x: {
            'fillColor': 'gray',
            'color': 'gray',
            'fillOpacity': 0.7,
            'weight': 0,
        }
    ).add_to(m)
     
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
    map_obj = create_interactive_map(
        osm_file_path='data/cologne.osm',
        boundary_geojson_path='data/cologne_boundary.json'
    )
    map_obj.save('index.html')

if __name__ == "__main__":
    main()