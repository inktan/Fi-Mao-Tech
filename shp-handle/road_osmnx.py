import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
from coord_convert import transform

# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [
(111.69235154492786,40.790409462215635),
(111.69439295429582,40.785869224573254),
(111.67441733619775,40.780234796050514),
(111.67153384581377,40.78697799220351),
]
# 将 GCJ-02 坐标转换为 WGS84 坐标
wgs_coords = [transform.gcj2wgs(lng, lat) for lng, lat in coords]
polygon = Polygon(wgs_coords)

# 为指定的多边形区域下载路网数据
# G = ox.graph_from_polygon(polygon, network_type='drive')
G = ox.graph_from_polygon(polygon, network_type='all')

# 将图转换为 GeoDataFrame
gdf = ox.graph_to_gdfs(G, nodes=False)

# 定义保存 SHP 文件的文件路径
file_path = "E:\work\sv_aaalingnanlizhiwangge\street_network.shp"
gdf.to_file(file_path)

