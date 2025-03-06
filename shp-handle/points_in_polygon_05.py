import geopandas as gpd

import geopandas as gpd
from shapely.geometry import Polygon

# 定义多边形顶点坐标
coords = [
    ( 108.93793945745632 ,34.257570394616096),
    ( 108.93777852493311 ,34.26446019711957),
    ( 108.94674783089218 ,34.2645311316619),
    ( 108.94690876341534 ,34.25748171909102),
]

# 创建 Polygon 对象
polygon = Polygon(coords)

# 创建 GeoDataFrame
gdf = gpd.GeoDataFrame(geometry=[polygon])
gdf = gdf.set_crs("EPSG:4326")

gdf.to_file(r'E:\work\sv_lvmaoshuiguai\fanwei02.shp')

# point_gdf = gpd.read_file(r'e:\work\sv_juanjuanmao\20250223\澳门POI2022\ShapeFile\澳门特别行政区_购物服务_20220103_145740.shp')
# spatial_join_result = gpd.sjoin(point_gdf, polygon_gdf, predicate='within')
# spatial_join_result.to_file(f'E:\work\sv_juanjuanmao\\20250223\\results\购物服务_in_T{i}.shp')
# spatial_join_result.to_csv(f'E:\work\sv_juanjuanmao\\20250223\\results\购物服务_in_T{i}.csv')
# print(f"保存了 {len(spatial_join_result)} 个落在多边形内的点")
