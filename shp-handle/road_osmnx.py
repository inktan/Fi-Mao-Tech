import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
from coord_convert import transform
import matplotlib.pyplot as plt
# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [
(104.04547548323656,30.73204069252845),
(104.08990163201774,30.728493179131913),
(104.15763330147104,30.714301819938864),
(104.16710116924408,30.70261325000745),
(104.17074265684909,30.670462381670706),
(104.16491627668105,30.64268710914986),
(104.14913649705932,30.610307363297096),
(104.13894033176527,30.59923309396694),
(104.13384224911826,30.596934502107242),
(104.09669907554711,30.58711263175359),
(104.04231952731222,30.592337154799104),
(104.00517635374106,30.614068147560218),
(103.97895764298495,30.6424782420607),
(103.97361679449759,30.661065626206426),
(103.98381295979163,30.681110932590347),
(104.00590465117703,30.710127493260515),
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
file_path = r"E:\work\sv_michinen\_network.shp"
gdf.to_file(file_path)
