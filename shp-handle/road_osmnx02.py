import geopandas as gpd
from shapely.ops import unary_union
import osmnx as ox
import os
from shapely.geometry import Polygon, MultiLineString
from shapely.ops import polygonize, unary_union
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon, box
from coord_convert import transform
import matplotlib.pyplot as plt
import math
import time
import os
import pandas as pd
from shapely.ops import unary_union

# 1. 读取原始 SHP 文件并合并所有多边形
input_shp = r"e:\work\20250709_sv_michinen\20251021\乡镇级行政区划合集02.shp"  # 替换为你的输入文件路径
gdf = gpd.read_file(input_shp)

# 基本绘图
# gdf.plot()
# plt.title("SHP文件几何图形")
# plt.show()

# 确保是WGS84 (EPSG:4326)坐标系
if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs('EPSG:4326')
print(gdf.crs)

# 2. 检查几何类型是否为多边形
if not all(gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])):
    raise ValueError("输入SHP文件必须只包含多边形要素")

# 3. 合并所有多边形为一个
# merged_polygon = gdf.unary_union

# 2. 筛选 "县名列" 为 "蒸湘区" 的行
# filtered_gdf = gdf[gdf["县名"] == "锦江区"]
filtered_gdf = gdf

# 合并所有几何体为一个多边形
merged_polygon = unary_union(filtered_gdf.geometry)

# 3. 获取筛选后的 Polygon 数据
# if not filtered_gdf.empty:
#     merged_polygon = filtered_gdf.geometry.iloc[0]  # 获取第一个匹配的 Polygon

# 可选：可视化
filtered_gdf.plot()  # 使用 matplotlib 绘制图形

# 4. 简化多边形（可选，对于复杂多边形可以提高性能）
# merged_polygon = merged_polygon.simplify(tolerance=0.001)

# 2. 使用OSMnx获取该区域内的路网
G = ox.graph_from_polygon(merged_polygon, network_type='all')

# 3. 将图转换为GeoDataFrame并保存
gdf_edges = ox.graph_to_gdfs(G, nodes=False)

# 定义保存路径
output_shp = r'e:\work\20250709_sv_michinen\20251021\乡镇级行政区划合集02_netroad.shp'
# output_shp = input_shp.replace('.shp','_netroad.shp')

# 确保输出目录存在
os.makedirs(os.path.dirname(output_shp), exist_ok=True)

# 保存为SHP文件
gdf_edges.to_file(output_shp, encoding='utf-8')

print(f"路网数据已成功保存到 {output_shp}")


