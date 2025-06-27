import geopandas as gpd
from shapely.ops import unary_union
import osmnx as ox
import os
from shapely.geometry import Polygon, MultiLineString
from shapely.ops import polygonize, unary_union

# 1. 读取原始 SHP 文件并合并所有多边形
input_shp = r"e:\work\sv_qingningmigucheng\主城区\主城区.shp"  # 替换为你的输入文件路径
gdf = gpd.read_file(input_shp)

# 确保是WGS84 (EPSG:4326)坐标系
if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs('EPSG:4326')
print(gdf.crs)

lines = gdf[gdf.geometry.type == 'LineString'].geometry.tolist()
# 转换 LineString 为 Polygon（强制闭合）
polygons = []
for line in lines:
    if line.geom_type == 'LineString':
        if line.is_closed:
            polygons.append(Polygon(line))
        else:
            # 方法1：强制闭合
            coords = list(line.coords)
            coords[-1] = coords[0]  # 闭合线段
            polygons.append(Polygon(coords))
# 合并所有多边形
merged_polygon = unary_union(polygons)

# 2. 使用OSMnx获取该区域内的路网
G = ox.graph_from_polygon(merged_polygon, network_type='all')

# 3. 将图转换为GeoDataFrame并保存
gdf_edges = ox.graph_to_gdfs(G, nodes=False)

# 定义保存路径
output_shp = input_shp.replace('.shp','_netroad.shp')

# 确保输出目录存在
os.makedirs(os.path.dirname(output_shp), exist_ok=True)

# 保存为SHP文件
gdf_edges.to_file(output_shp, encoding='utf-8')

print(f"路网数据已成功保存到 {output_shp}")