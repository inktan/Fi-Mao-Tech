import geopandas as gpd
from shapely.geometry import Polygon

shp_file_path = r'e:\work\sv_小丸\福田区面\福田区面.shp'
shp_file_path = r'h:\地学大数据\2024年5月全国路网数据\2024年5月全国路网数据_分省市\广东省\深圳市.shp'
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

# Bottom-left corner: (331967.4528198242, 3428347.637084961)
# Bottom-right corner: (377833.63494873047, 3428347.637084961)
# Top-left corner: (331967.4528198242, 3476996.5552368164)
# Top-right corner: (377833.63494873047, 3476996.5552368164)

# 显示所有列的名称
print(gdf.columns)

# 获取特定的列
# print(gdf['column_name'])

# 或者你可以进行更复杂的数据操作，比如筛选特定的行
# filtered_gdf = gdf[gdf['column_name'] == 'some_value']
# print(filtered_gdf)







