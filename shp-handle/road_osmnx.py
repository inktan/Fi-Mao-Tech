import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
from coord_convert import transform
import matplotlib.pyplot as plt
# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [
(127.0425641373654,27.222612386621773),
(128.97800117631277,27.212343057322926),
(128.8186394153493,25.757087779323715),
(127.09568472435322,25.769567845488016),
]
# 在google map上获取的国内经纬度点需要从 GCJ-02 坐标转换为 WGS84
# coords = [transform.gcj2wgs(lng, lat) for lng, lat in coords]
polygon = Polygon(coords)
fig, ax = plt.subplots(figsize=(10, 8))
x, y = polygon.exterior.xy
ax.fill(x, y, alpha=0.5, fc='blue', ec='black')
ax.set_title('Polygon from WGS84 Coordinates')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.grid(True)
plt.tight_layout()
plt.show()

# 为指定的多边形区域下载路网数据
# G = ox.graph_from_polygon(polygon, network_type='drive')
G = ox.graph_from_polygon(polygon, network_type='all')

# 将图转换为 GeoDataFrame
gdf = ox.graph_to_gdfs(G, nodes=False)

# 定义保存 SHP 文件的文件路径
file_path = r"E:\work\sv_huammengmaomao\冲绳\_network01.shp"
gdf.to_file(file_path)
