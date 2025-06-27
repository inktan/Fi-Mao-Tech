import geopandas as gpd
from coord_convert import transform
from shapely.geometry import Point, LineString, LinearRing, Polygon
from tqdm import tqdm

def wgs84_to_bd09_coords(lon, lat):
    """使用coord_convert库将WGS84坐标转换为BD09坐标"""
    return transform.wgs2bd(lon, lat)

def transform_geometry(geom):
    """递归处理几何对象中的所有坐标点"""
    if geom.is_empty:
        return geom
    
    if geom.geom_type == 'Point':
        # 转换单个点
        x, y = geom.x, geom.y
        new_x, new_y = wgs84_to_bd09_coords(x, y)
        return Point(new_x, new_y)
    elif geom.geom_type in ['LineString', 'LinearRing']:
        # 转换线
        points = list(geom.coords)
        new_points = [wgs84_to_bd09_coords(x, y) for x, y in points]
        return LineString(new_points) if geom.geom_type == 'LineString' else LinearRing(new_points)
    elif geom.geom_type == 'Polygon':
        # 转换多边形
        exterior = transform_geometry(geom.exterior)
        interiors = [transform_geometry(ring) for ring in geom.interiors]
        return Polygon(exterior, interiors)
    elif geom.geom_type.startswith('Multi') or geom.geom_type == 'GeometryCollection':
        # 转换多几何对象
        parts = [transform_geometry(part) for part in geom.geoms]
        return type(geom)(parts)
    else:
        raise ValueError(f"不支持的几何类型: {geom.geom_type}")

# 输入输出文件路径
input_shp = r"e:\work\sv_xiufenganning\road\_network.shp"  # 替换为你的输入文件(WGS84坐标系)
output_shp = r"e:\work\sv_xiufenganning\road\_network_bd09.shp"  # 替换为你的输出文件(BD09坐标系)

print("正在读取SHP文件...")
gdf = gpd.read_file(input_shp)

# 确保原始坐标系是WGS84 (EPSG:4326)
if gdf.crs is None or str(gdf.crs).upper() != "EPSG:4326":
    print("警告: 输入文件的坐标系可能不是WGS84 (EPSG:4326)，请确认数据源坐标系!")

print("正在转换坐标系(WGS84 -> BD09)...")
# 应用坐标转换到所有几何对象
tqdm.pandas(desc="转换进度")
gdf['geometry'] = gdf['geometry'].progress_apply(transform_geometry)

# 更新坐标系信息(BD09没有标准EPSG代码，可以设为None或保留原CRS)
gdf.crs = None  # 或者 gdf.crs = "EPSG:4326" 但注明实际是BD09

print("正在保存转换后的文件...")
gdf.to_file(output_shp, encoding='utf-8')

print(f"转换完成! 结果已保存到 {output_shp}")