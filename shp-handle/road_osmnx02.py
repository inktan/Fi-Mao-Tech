import geopandas as gpd
from shapely.ops import unary_union
import osmnx as ox
import os

# 1. 读取原始 SHP 文件并合并所有多边形
input_shp = r"e:\work\sv_momo\sv_20250512\sv_20250512.shp"  # 替换为你的输入文件路径
gdf = gpd.read_file(input_shp)

# 确保所有几何体都是多边形
polygons = gdf[gdf.geometry.type == 'Polygon'].geometry.tolist()

if not polygons:
    raise ValueError("输入SHP文件中没有找到多边形几何体")

# 合并所有多边形为一个大的多边形
merged_polygon = unary_union(polygons)

# 2. 使用OSMnx获取该区域内的路网
G = ox.graph_from_polygon(merged_polygon, network_type='all')

# 3. 将图转换为GeoDataFrame并保存
gdf_edges = ox.graph_to_gdfs(G, nodes=False)

# 定义保存路径
output_shp = r"E:\work\sv_momo\sv_20250512\street_network.shp"  # 替换为你想要的输出路径

# 确保输出目录存在
os.makedirs(os.path.dirname(output_shp), exist_ok=True)

# 保存为SHP文件
gdf_edges.to_file(output_shp, encoding='utf-8')

print(f"路网数据已成功保存到 {output_shp}")