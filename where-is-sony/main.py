import geopandas as gpd
import matplotlib.pyplot as plt

shape_path = gpd.read_file('/home/thea/Dokumente/GitHub/where-is-sony/where-is-sony/cologne_shapefiles/Stadtviertel.shp')

print(shape_path.head())

shape_path.plot(cmap = 'jet')

plt.show()