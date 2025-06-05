import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
from coord_convert import transform
import matplotlib.pyplot as plt
# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [

(114.253918,30.613739),
(114.328707,30.638645),
(114.332882,30.63738),
(114.359738,30.618792),
(114.38031,30.583506),
(114.35583,30.544722),
(114.358154,30.549498),
(114.355011,30.546746),
(114.354158,30.544296),
(114.35847,30.536115),
(114.35847,30.536115),
(114.34833,30.50923),
(114.338824,30.510823),
(114.333597,30.515239),
(114.302415,30.525944),
(114.294915,30.524804),
(114.271081,30.536712),
(114.252411,30.536336),
(114.240503,30.547847),
(114.237167,30.549599),
(114.250022,30.569959),
(114.251125,30.58364),
(114.249253,30.591624),
(114.253732,30.605819),
(114.249283,30.613062),

]

# 将 GCJ-02 坐标转换为 WGS84 坐标
wgs_coords = [transform.gcj2wgs(lng, lat) for lng, lat in coords]
polygon = Polygon(wgs_coords)
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
file_path = r"E:\work\sv_xiufenganning\road\_network.shp"
gdf.to_file(file_path)
