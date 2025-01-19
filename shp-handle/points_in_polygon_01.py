
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm
import os

shp_path  = r'e:\work\sv_hukejia\sv\handle\points01_panoid02_toshp\merged_output.shp'

points_gdf  = gpd.read_file(shp_path)
print(shp_path,points_gdf.shape)

# 读取第二个shapefile（排除的多边形）
polygons_shp_path  = r'e:\work\sv_hukejia\map\bufferzone1km.shp'
polygons_gdf  = gpd.read_file(polygons_shp_path)
print(polygons_shp_path,polygons_shp_path.shape)

# 确保多边形和点的坐标参考系统一致
if points_gdf.crs != polygons_gdf.crs:
    polygons_gdf = polygons_gdf.to_crs(points_gdf.crs)

# 准备一个字典来存储每个多边形包含的点的数量
polygons_with_points = {}

# 创建一个空的 GeoDataFrame 来存储合并后的点数据
merged_points_in_gdf = gpd.GeoDataFrame(columns=['geometry'])

# 初始化新列，默认值为0
polygons_gdf['points_count'] = 0
# 遍历每个多边形
for index, polygon in tqdm(polygons_gdf.iterrows()):
    # 跳过多边形几何对象为空的记录
    if polygon.geometry is None:
        polygons_gdf.at[index, 'points_count'] = 0
        polygons_with_points[index] = 0
        continue
    # 使用within方法找出位于多边形内的点
    points_within_polygon = points_gdf[points_gdf.geometry.within(polygon.geometry)]
    # 将点数据添加到合并后的 GeoDataFrame
    if not points_within_polygon.empty:
        merged_points_in_gdf = merged_points_in_gdf._append(points_within_polygon)

    # 记录当前多边形包含的点的数量到新列
    polygons_gdf.at[index, 'points_count'] = len(points_within_polygon)

    polygons_with_points[index] = len(points_within_polygon)
    if len(points_within_polygon)>0:
        print(len(points_within_polygon))

polygons_gdf.to_file(polygons_shp_path.replace('.shp','_01.shp'))

# 输出结果
# for poly_index, points_count in polygons_with_points.items():
#     print(f"多边形 {poly_index} 包含 {points_count} 个点。")

# 如果需要统计有多少个多边形至少包含一个点
polygons_with_at_least_one_point = sum(1 for count in polygons_with_points.values() if count > 0)
print(f"总共有 {polygons_with_at_least_one_point} 个多边形中至少包含一个点。")

# 将合并后的 GeoDataFrame 导出为 SHP 文件
output_path = shp_path.replace('.shp', '_in.shp')
merged_points_in_gdf.to_file(output_path)