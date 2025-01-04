import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 读取CSV文件
csv_file = 'your_points.csv'
df = pd.read_csv(csv_file)

# 假设CSV文件中有'lon'和'lat'列
# 创建一个GeoDataFrame
geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
gdf_points = gpd.GeoDataFrame(df, geometry=geometry)

# 读取第一个shapefile（包含的多边形）
shapefile_include = 'include_polygon.shp'
gdf_include_polygon = gpd.read_file(shapefile_include)
include_polygon = gdf_include_polygon.geometry.unary_union

# 读取第二个shapefile（排除的多边形）
shapefile_exclude = 'exclude_polygon.shp'
gdf_exclude_polygon = gpd.read_file(shapefile_exclude)
exclude_polygon = gdf_exclude_polygon.geometry.unary_union

# 检查每个点是否在包含多边形中且不在排除多边形中
gdf_points['in_include_polygon'] = gdf_points.within(include_polygon)
gdf_points['in_exclude_polygon'] = gdf_points.within(exclude_polygon)

# 过滤出在包含多边形内且不在排除多边形内的点
gdf_points_filtered = gdf_points[gdf_points['in_include_polygon'] & ~gdf_points['in_exclude_polygon']]

# 保存结果到新的CSV文件
output_csv_file = 'filtered_points.csv'
gdf_points_filtered.drop(columns='geometry').to_csv(output_csv_file, index=False)

print(f"Filtered points saved to {output_csv_file}")