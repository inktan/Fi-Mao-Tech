import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
from coord_convert import transform
import matplotlib.pyplot as plt
# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [
(120.1172977224243,30.28851773123559),
(120.13669110872091,30.289839784863418),
(120.1379159541712,30.276177704885466),
(120.11801221560363,30.274943616897385),
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
file_path = r"E:\work\sv_momo\street_network.shp"
gdf.to_file(file_path)


