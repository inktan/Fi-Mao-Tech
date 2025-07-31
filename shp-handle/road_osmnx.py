import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
from coord_convert import transform
import matplotlib.pyplot as plt
# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [
(116.27836239314846,39.986646073705586),
(116.3037682746746,39.990591738407375),
(116.44178400945162,39.993748106074676),
(116.44659052757818,39.99111780981464),
(116.49122248161056,39.96138842309896),
(116.49568567701381,39.952967132054965),
(116.49465570884382,39.84761351500988),
(116.46890650459437,39.829423638028814),
(116.37346278750975,39.8286326645224),
(116.28728878395493,39.8286326645224),
(116.27836239314846,39.82995094864025),
(116.27218258412859,39.86922420478426),
(116.26806271144868,39.88687666743881),
(116.26977932506533,39.96717745912412),
(116.27492916591521,39.977175548586075),
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
file_path = r"E:\work\sv_carol\_network.shp"
gdf.to_file(file_path)
