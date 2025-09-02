import geopandas as gpd
from coord_convert import transform  # 需要安装coord_convert库
from shapely.geometry import Point,LineString,Polygon

# 读取shp文件
gdf = gpd.read_file(r"e:\work\sv_xiufenganning\20250819\ade_20k_语义分割比例数据_01-_.shp")

# 确保是WGS84坐标系
if gdf.crs != "EPSG:4326":
    gdf = gpd.to_crs("EPSG:4326")

# 定义转换函数
def wgs_to_gcj(geom):
    if geom.geom_type == "Point":
        x, y = transform.wgs2bd(geom.x, geom.y)
        return Point(x, y)
    elif geom.geom_type == "LineString":
        points = [transform.wgs2bd(*coord) for coord in geom.coords]
        return LineString(points)
    elif geom.geom_type == "Polygon":
        ext = [transform.wgs2bd(*coord) for coord in geom.exterior.coords]
        holes = [[transform.wgs2bd(*coord) for coord in interior.coords] 
                for interior in geom.interiors]
        return Polygon(ext, holes)
    else:
        return geom

# 应用转换
gdf["geometry"] = gdf["geometry"].apply(wgs_to_gcj)

# 保存结果
gdf.to_file(r"e:\work\sv_xiufenganning\20250819\ade_20k_语义分割比例数据_01-_bd09.shp")
print("转换完成！")