import osmnx as ox
import folium
from folium import plugins
import geopandas as gpd
import branca.colormap as cm

def create_interactive_map(osm_file_path):
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
            show=False  # Only show on closer zoom
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
    
    # Add custom CSS for label styling
    style = """
    <style>
        .street-label {
            background: none;
            border: none;
            box-shadow: none;
            font-size: 12px;
            font-weight: bold;
            color: #555;
            text-shadow: 1px 1px 1px #fff;
        }
        @media (max-width: 1200px) {
            .street-label {
                display: none;
            }
        }
    </style>
    """
    
    m.get_root().html.add_child(folium.Element(style))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

# Use the function
map_obj = create_interactive_map('/home/thea/Dokumente/GitHub/where-is-sony/cologne_shapefiles/bayenthal.osm')
map_obj.save('cologne_bayenthal_interactive.html')
