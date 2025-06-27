import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
from coord_convert import transform
import matplotlib.pyplot as plt
# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [
(139.63176155736613,35.46870710426971),
( 139.63364299273886,35.465395286282536),
(139.63509958786608,35.46455495256419),
( 139.6400459421524,35.464159498364616),
(139.64071354825236,35.46178673233706),
( 139.6392569531251,35.459389178906186),
( 139.63907487873422,35.456966835864016),
(139.63613134274792,35.45585451105275),
(139.63412852444793,35.45382756852051),
(139.63406783297444,35.44893303331136),
(139.63154913725052,35.44732617652869),
(139.6253889536915,35.45580507395063),
(139.6229006037003,35.45998239460451),
(139.622779220773,35.46260237850305),
(139.6236289013351,35.46406063453944),
(139.62866629281686,35.46618618061379),
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
file_path = r"E:\work\sv_gonhoo\_network.shp"
gdf.to_file(file_path)
