import geopandas as gpd
from shapely.affinity import translate
import geopandas as gpd
from shapely.geometry import Polygon

# 定义多边形顶点坐标
coords = [
(111.69235154492786,40.790409462215635),
(111.69439295429582,40.785869224573254),
(111.67441733619775,40.780234796050514),
(111.67153384581377,40.78697799220351),
]

# 创建 Polygon 对象
polygon = Polygon(coords)

# 定义平移向量 (x_offset, y_offset) google经纬度与osm路网的经纬度有偏移
translation_vector = (-0.006793612088074497, -0.0012703673607319388)

# 平移多边形
translated_polygon = translate(polygon, xoff=translation_vector[0], yoff=translation_vector[1])


# 创建 GeoDataFrame
# gdf = gpd.GeoDataFrame(geometry=[polygon])
# gdf = gdf.set_crs("EPSG:4326")

# gdf.to_file(r'E:\work\sv_aaalingnanlizhiwangge\fanwei02.shp')

# point_gdf = gpd.read_file(r'e:\work\sv_juanjuanmao\20250223\澳门POI2022\ShapeFile\澳门特别行政区_购物服务_20220103_145740.shp')
# spatial_join_result = gpd.sjoin(point_gdf, polygon_gdf, predicate='within')
# spatial_join_result.to_file(f'E:\work\sv_juanjuanmao\\20250223\\results\购物服务_in_T{i}.shp')
# spatial_join_result.to_csv(f'E:\work\sv_juanjuanmao\\20250223\\results\购物服务_in_T{i}.csv')
# print(f"保存了 {len(spatial_join_result)} 个落在多边形内的点")

# osm路网经纬度定位
# 111.675652  40.782094 
# google map经纬度定位
# 111.68244561208807,40.78336436736073

# 经纬度差值
# (-0.006793612088074497,-0.0012703673607319388)

from coord_convert import transform

# GCJ-02 坐标（Google 地图）
gcj_lng, gcj_lat = 111.68244561208807,40.78336436736073

# 转换为 WGS84 坐标
wgs_lng, wgs_lat = transform.gcj2wgs(gcj_lng, gcj_lat)

print(f"GCJ-02 坐标: ({gcj_lng}, {gcj_lat})")
print(f"WGS84 坐标: ({wgs_lng}, {wgs_lat})")