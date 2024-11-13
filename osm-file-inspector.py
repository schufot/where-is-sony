import xml.etree.ElementTree as ET

def inspect_osm_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Count elements
    nodes = root.findall(".//node")
    ways = root.findall(".//way")
    relations = root.findall(".//relation")
    
    print(f"Number of nodes: {len(nodes)}")
    print(f"Number of ways: {len(ways)}")
    print(f"Number of relations: {len(relations)}")
    
    # Check for specific tags
    buildings = root.findall(".//tag[@k='building']")
    highways = root.findall(".//tag[@k='highway']")
    
    print(f"Number of buildings: {len(buildings)}")
    print(f"Number of highways: {len(highways)}")

# Use the function
inspect_osm_file('/home/thea/Dokumente/GitHub/where-is-sony/where-is-sony/cologne_shapefiles/bayenthal.osm')