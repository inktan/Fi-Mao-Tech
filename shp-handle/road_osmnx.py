import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
from coord_convert import transform
import matplotlib.pyplot as plt
# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [
(113.53250016371473,22.181140459506132),
(113.53771962963158,22.185973574958727),
(113.53905484184287,22.190385052647752),
(113.54060247417868,22.192042833290838),
(113.54360670165407,22.192801472144044),
(113.54442603642009,22.197409412692405),
(113.54345497298222,22.20513580292119),
(113.53735548083522,22.20488294597244),
(113.53826585279745,22.197297025719344),
(113.53468505641264,22.19139658216867),
(113.52946559049578,22.186760345482607),
(113.52894971305052,22.181814857710247),

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
file_path = r"E:\work\sv_npc\_network.shp"
gdf.to_file(file_path)
