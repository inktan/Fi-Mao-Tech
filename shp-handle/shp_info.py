import geopandas as gpd
from shapely.geometry import Polygon

shp_file_path = r'e:\work\苏大-鹌鹑蛋好吃\研究边界\Export_Output_8\Export_Output_8.shp'
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

# Bottom-left corner: (331967.4528198242, 3428347.637084961)
# Bottom-right corner: (377833.63494873047, 3428347.637084961)
# Top-left corner: (331967.4528198242, 3476996.5552368164)
# Top-right corner: (377833.63494873047, 3476996.5552368164)






