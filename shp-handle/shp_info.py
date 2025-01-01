import geopandas as gpd
from shapely.geometry import Polygon

shp_file_path = r'e:\work\sv_小丸\福田区面\福田区面.shp'
gdf = gpd.read_file(shp_file_path)

geometry = gdf.geometry

bounding_box = geometry[0].bounds

minx, miny, maxx, maxy = bounding_box

bottom_left = (minx, miny)
bottom_right = (maxx, miny)
top_left = (minx, maxy)
top_right = (maxx, maxy)

print(f"Bottom-left corner: {bottom_left}")
print(f"Bottom-right corner: {bottom_right}")
print(f"Top-left corner: {top_left}")
print(f"Top-right corner: {top_right}")

print(gdf.head())

