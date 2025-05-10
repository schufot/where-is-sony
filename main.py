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

        if not data.get("features") or len(data["features"]) == 0:
            print(f"ERROR: GeoJSON file {filepath} has no features")
            raise ValueError("Invalid GeoJSON: No features found")
            
        # Take the first feature's ring as the main polygon
        rings = data["features"][0]["geometry"].get("rings")
        if not rings or len(rings) == 0:
            print(f"ERROR: GeoJSON feature has no rings at {filepath}")
            raise ValueError("Invalid GeoJSON: No rings found in feature")
            
        # ESRI GeoJSON has longitude,latitude ordering
        try:
            polygon = Polygon(rings[0])
            
            # Create a GeoDataFrame with EPSG:4326
            gdf = gpd.GeoDataFrame(geometry=[polygon], crs="EPSG:4326")
            bounds = gdf.total_bounds
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

def get_all_points():
    """Retrieve all points from the database"""
    try:
        conn = sqlite3.connect('map_points.db')
        c = conn.cursor()
        
        c.execute('SELECT * FROM points')
        points = c.fetchall()
        
        conn.close()
        print(f"Retrieved {len(points)} points from database")
        return points
    except Exception as e:
        print(f"Error retrieving points from database: {e}")
        return []

def create_interactive_map(osm_file_path, boundary_geojson_path):
    """
    Create an interactive folium map showing only Cologne, masking the rest of the world.
    """
    print("DEBUG: Starting map creation...")
    
    # Verify files exist
    if not os.path.exists(osm_file_path):
        print(f"ERROR: OSM file not found at {osm_file_path}")
        raise FileNotFoundError(f"OSM file not found: {osm_file_path}")
        
    if not os.path.exists(boundary_geojson_path):
        print(f"ERROR: Boundary GeoJSON not found at {boundary_geojson_path}")
        raise FileNotFoundError(f"Boundary file not found: {boundary_geojson_path}")
    
    print(f"DEBUG: Loading boundary from {boundary_geojson_path}")
    # Load and convert the ESRI-style GeoJSON
    boundary = convert_esri_geojson_to_polygon(boundary_geojson_path)

    # Get the bounds of Cologne
    bounds = boundary.total_bounds
    # In GeoDataFrame total_bounds, the order is [xmin, ymin, xmax, ymax] 
    # which is [west, south, east, north]
    west, south, east, north = bounds
    print(f"DEBUG: Boundary bounds - West:{west}, South:{south}, East:{east}, North:{north}")

    # Create a base map centered on Cologne
    cologne_center = [south + (north - south)/2, west + (east - west)/2]
    print(f"DEBUG: Creating map centered at {cologne_center}")
    
    # Create map with explicit tile layer
    m = folium.Map(
        location=cologne_center, 
        zoom_start=12,
        tiles='OpenStreetMap',
        prefer_canvas=True
    )
    
    # Add coordinates display box to the map
    coordinates_div_html = """
    <div id="coordinates-box" style="
        position: fixed;
        bottom: 20px;
        left: 20px;
        background-color: white;
        padding: 10px;
        border-radius: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        z-index: 1000;
        font-family: Arial, sans-serif;
        font-size: 12px;
        display: none;
    ">
        <strong>Clicked Coordinates:</strong> <span id="coordinates"></span>
    </div>
    """
    
    # Add the HTML element to the map
    m.get_root().html.add_child(folium.Element(coordinates_div_html))
    
    # Create custom JavaScript for handling clicks
    click_script = """
    <script>
        // Function to handle map click events
        function handleMapClick(e) {
            // Format the coordinates with 6 decimal places
            var lat = e.latlng.lat.toFixed(6);
            var lng = e.latlng.lng.toFixed(6);
            
            // Get the coordinates display element
            var coordBox = document.getElementById('coordinates-box');
            var coordDisplay = document.getElementById('coordinates');
            
            // Update and show the coordinates box
            if (coordDisplay && coordBox) {
                coordDisplay.textContent = lat + ", " + lng;
                coordBox.style.display = "block";
                
                // Copy to clipboard if available
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(lat + ", " + lng);
                }
            } else {
                console.error("Coordinates display elements not found");
            }
        }
        
        // Wait for the map to be fully loaded
        window.addEventListener('load', function() {
            console.log("Window loaded, setting up click handler");
            setTimeout(function() {
                // Get the map object
                var mapContainer = document.getElementsByClassName('folium-map')[0];
                if (mapContainer && mapContainer._leaflet_id) {
                    // Access the Leaflet map instance
                    var leafletMap = window.L.Map.getMapById(mapContainer._leaflet_id);
                    if (leafletMap) {
                        console.log("Adding click handler to map");
                        leafletMap.on('click', handleMapClick);
                    } else {
                        console.error("Could not get Leaflet map instance");
                    }
                } else {
                    console.error("Map container not found or not initialized");
                }
            }, 1000); // Give the map a second to fully initialize
        });
    </script>
    """
    
    # Add the script to the head of the document
    m.get_root().header.add_child(folium.Element(click_script))
    
    try:
        print(f"DEBUG: Loading OSM data from {osm_file_path}")
        # Load OSM data - with error handling
        graph = ox.graph_from_xml(osm_file_path)
        nodes, edges = ox.graph_to_gdfs(graph)
        print(f"DEBUG: Loaded {len(edges)} edges from OSM")
        
        # Add streets to the map - can be commented out if causing performance issues
        folium.GeoJson(
            edges.to_json(),
            name="Streets",
            style_function=lambda x: {
                'color': 'black',
                'weight': 1,
                'opacity': 0.7
            }
        ).add_to(m)
    except Exception as e:
        print(f"ERROR loading OSM data: {e}")
        print("Continuing without OSM data...")
    
    # Set map bounds to the Cologne boundary - CORRECTED ORDER
    # Folium's fit_bounds expects [[south, west], [north, east]]
    print("DEBUG: Setting map bounds to [[south, west], [north, east]]")
    m.fit_bounds([[south, west], [north, east]])
    
    # Add the Cologne boundary itself
    folium.GeoJson(
        boundary,
        name="Cologne Boundary",
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'blue',
            'weight': 2,
        }
    ).add_to(m)
    
    # Create a world bounding box for the mask
    print("DEBUG: Creating mask overlay")
    world = gpd.GeoDataFrame(geometry=[box(-180, -90, 180, 90)], crs="EPSG:4326")
    
    try:
        # Create a mask: World minus Cologne
        mask = gpd.overlay(world, boundary, how="difference")
        
        # Add the gray mask outside Cologne - setting opacity much lower to see through it
        folium.GeoJson(
            mask,
            name="Outside Cologne",
            style_function=lambda x: {
                'fillColor': 'gray',
                'color': 'gray',
                'fillOpacity': 0.3,  # Lower opacity
                'weight': 0,
            }
        ).add_to(m)
    except Exception as e:
        print(f"ERROR creating mask overlay: {e}")
        print("Continuing without mask...")
    
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
    print("DEBUG: Adding points from database")
    points = get_all_points()
    for point in points:
        id, lat, lon, description, image_path, created_at = point
        
        # Verify image exists
        if not os.path.exists(image_path):
            print(f"WARNING: Image not found at {image_path} for point {id}")
            img_html = f"<p>Image not found: {image_path}</p>"
        else:
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
        
        # Changed from Marker to CircleMarker for small red circles
        folium.CircleMarker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=250),
            radius=5,  # Size of the circle in pixels
            color='red',  # Circle outline color
            fill=True,
            fill_color='red',  # Circle fill color
            fill_opacity=0.7,
            weight=1  # Border weight
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add Leaflet.js click handler via Folium's built-in method
    folium.JavascriptLink(
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.js"
    ).add_to(m)
    
    # Add a click handler using Folium's callback mechanism
    click_handler = """
        function (e) {
            // Get clicked coordinates
            var lat = e.latlng.lat.toFixed(6);
            var lng = e.latlng.lng.toFixed(6);
            
            // Create a popup at the clicked location
            L.popup()
                .setLatLng(e.latlng)
                .setContent("Latitude: " + lat + "<br>Longitude: " + lng)
                .openOn(this);
                
            // Copy to clipboard if supported
            if (navigator.clipboard) {
                navigator.clipboard.writeText(lat + ", " + lng);
                console.log("Coordinates copied to clipboard");
            }
        }
    """
    
    # Add the click handler directly to the map object
    m.add_child(folium.LatLngPopup())
    
    print("DEBUG: Map creation complete")
    return m