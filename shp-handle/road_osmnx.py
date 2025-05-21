import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
from coord_convert import transform
import matplotlib.pyplot as plt
# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [

( 108.94207799311776,34.26480441563007),
( 108.94448125213071,34.26476894848164),
( 108.94479238834221,34.263500988099416),
( 108.94584381416037,34.26346552040133),
( 108.945521949114,34.26018469364981),
( 108.94425594659826,34.26015809182884),
( 108.9441808447541,34.259776798136976),
(  108.94283974039418,34.25983886932089),
( 108.94270026554075,34.2604861803663),
(108.9424213158339,34.26072559551846),
(108.94228184098047,34.26312857652336),
( 108.94241058699902,34.2640773360974),

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
file_path = r"E:\work\sv_zhaolu\roads\beiyuanmen_07_network.shp"
gdf.to_file(file_path)

