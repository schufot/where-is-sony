import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box, LineString
import numpy as np

def calculate_angle(line):
    """Calculate the angle of a line string."""
    x1, y1, x2, y2 = line.coords[0][0], line.coords[0][1], line.coords[-1][0], line.coords[-1][1]
    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
    return angle

def place_label(ax, text, line, fontsize=6, color='blue', bbox_props=None):
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
                bbox=bbox_props)
    return t

def get_name(name_value):
    """Handle both string and list name values."""
    if isinstance(name_value, list):
        return name_value[0] if name_value else None
    return name_value

# Customize the plot style
ox.config(log_console=True, use_cache=True)

# Load the .osm file
graph = ox.graph_from_xml('/home/thea/Dokumente/GitHub/where-is-sony/where-is-sony/cologne_shapefiles/cologne.osm')

# Convert the graph to GeoDataFrames
nodes, edges = ox.graph_to_gdfs(graph)

# Get the bounding box of the entire dataset
minx, miny, maxx, maxy = edges.total_bounds

# Create a GeoDataFrame from the bounding box
area = gpd.GeoDataFrame({'geometry': [box(minx, miny, maxx, maxy)]}, crs=edges.crs)

# Get building footprints
buildings = ox.geometries_from_xml('/home/thea/Dokumente/GitHub/where-is-sony/where-is-sony/cologne_shapefiles/cologne.osm', tags={'building': True})

# Create the plot
fig, ax = plt.subplots(figsize=(15, 15))

# Plot the area boundary
area.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=2)

# Plot buildings
if not buildings.empty:
    buildings.plot(ax=ax, facecolor='lightgrey', edgecolor='dimgrey')

# Plot streets
edges.plot(ax=ax, linewidth=1, edgecolor='#BC8F8F')

# Annotate street names
labeled_streets = set()
bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.7)

for index, row in edges.iterrows():
    name = get_name(row.get('name'))
    if name and name not in labeled_streets:
        # Simplify the geometry to get a single line for labeling
        simple_line = LineString([row['geometry'].coords[0], row['geometry'].coords[-1]])
        place_label(ax, name, simple_line, fontsize=8, color='blue', bbox_props=bbox_props)
        labeled_streets.add(name)

plt.title('Cologne')
ax.set_axis_off()
plt.tight_layout()
plt.show()

# Save as shapefiles for future use
edges.to_file('output_streets.shp', driver='ESRI Shapefile')
if not buildings.empty:
    buildings.to_file('output_buildings.shp', driver='ESRI Shapefile')
