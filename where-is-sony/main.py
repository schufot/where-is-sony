import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box, LineString
import contextily as ctx
import numpy as np

def get_name(name_value):
    """Handle both string and list name values."""
    if isinstance(name_value, list):
        return name_value[0] if name_value else None
    return name_value

def calculate_angle(line):
    """Calculate the angle of a line string."""
    x1, y1, x2, y2 = line.coords[0][0], line.coords[0][1], line.coords[-1][0], line.coords[-1][1]
    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
    return angle

def place_label(ax, text, line, fontsize=6, color='black', bbox_props=None):
    """Place a label along a line with the correct rotation."""
    angle = calculate_angle(line)
    midpoint = line.interpolate(0.5, normalized=True)

    # Adjust angle for readability
    if angle > 90:
        angle -= 180
    elif angle < -90:
        angle += 180

    t = ax.text(midpoint.x, midpoint.y, text, fontsize=fontsize, color=color,
                rotation=angle, rotation_mode='anchor', ha='center', va='center',
                bbox=bbox_props, zorder=6)
    return t

# Customize the plot style
ox.config(log_console=True, use_cache=True)

# Load the .osm file
graph = ox.graph_from_xml('/home/thea/Dokumente/GitHub/where-is-sony/where-is-sony/cologne_shapefiles/bayenthal.osm')

# Convert the graph to GeoDataFrames
nodes, edges = ox.graph_to_gdfs(graph)

# Ensure the CRS is set correctly (OpenStreetMap uses EPSG:4326)
edges = edges.to_crs(epsg=4326)

# Get the bounding box of the entire dataset
minx, miny, maxx, maxy = edges.total_bounds

# Create a GeoDataFrame from the bounding box
area = gpd.GeoDataFrame({'geometry': [box(minx, miny, maxx, maxy)]}, crs=edges.crs)

# Get various features
buildings = ox.features_from_xml('/home/thea/Dokumente/GitHub/where-is-sony/where-is-sony/cologne_shapefiles/bayenthal.osm', tags={'building': True})
green_areas = ox.features_from_xml('/home/thea/Dokumente/GitHub/where-is-sony/where-is-sony/cologne_shapefiles/bayenthal.osm', tags={'landuse': ['grass', 'park', 'forest']})
water_bodies = ox.features_from_xml('/home/thea/Dokumente/GitHub/where-is-sony/where-is-sony/cologne_shapefiles/bayenthal.osm', tags={'natural': 'water'})

# Ensure all features have the same CRS
buildings = buildings.to_crs(epsg=4326)
green_areas = green_areas.to_crs(epsg=4326)
water_bodies = water_bodies.to_crs(epsg=4326)

# Create the plot
fig, ax = plt.subplots(figsize=(15, 15))

# Plot the area boundary
area.plot(ax=ax, facecolor='none', edgecolor='none')

# Plot green areas
if not green_areas.empty:
    green_areas.plot(ax=ax, facecolor='#add19e', edgecolor='#8fc07f', alpha=0.7)

# Plot water bodies
if not water_bodies.empty:
    water_bodies.plot(ax=ax, facecolor='#aad3df', edgecolor='#7ab6d6', alpha=0.7)

# Plot buildings
if not buildings.empty:
    buildings.plot(ax=ax, facecolor='#d9d0c9', edgecolor='#beb7ae', alpha=0.7)

# Plot streets
edges.plot(ax=ax, linewidth=1, edgecolor='#a1a1a1')

# Add street labels
for idx, row in edges.iterrows():
    if 'name' in row and row['name'] is not None:
        name = get_name(row['name'])
        if isinstance(row['geometry'], LineString):
            place_label(ax, name, row['geometry'], fontsize=6, 
                        bbox_props=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))

# Add OpenStreetMap basemap
try:
    ctx.add_basemap(ax, crs=edges.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
except Exception as e:
    print(f"Failed to add basemap: {e}")
    print("Continuing without basemap...")

plt.title('Cologne - Bayenthal')
ax.set_axis_off()
plt.tight_layout()
plt.show()

# Save as shapefiles for future use
edges.to_file('output_streets.shp', driver='ESRI Shapefile')
if not buildings.empty:
    buildings.to_file('output_buildings.shp', driver='ESRI Shapefile')
if not green_areas.empty:
    green_areas.to_file('output_green_areas.shp', driver='ESRI Shapefile')
if not water_bodies.empty:
    water_bodies.to_file('output_water_bodies.shp', driver='ESRI Shapefile')