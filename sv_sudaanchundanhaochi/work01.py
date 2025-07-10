import geopandas as gpd
from shapely.geometry import shape, mapping
from shapely.ops import transform
import pyproj
from functools import partial

# 定义原始点和目标点
original_point = (115.505973, 31.228514)
target_point = (121.49114592882678, 31.240277814949344)

# 计算平移向量
dx = target_point[0] - original_point[0]
dy = target_point[1] - original_point[1]

# 定义输入和输出shp文件路径
input_shp_path = r"e:\work\苏大-鹌鹑蛋好吃\gis数据-wgs84_01\merged_output_100\merged_output_100.shp"
output_shp_path = r"e:\work\苏大-鹌鹑蛋好吃\gis数据-wgs84\merged_output_100\merged_output_100.shp"

# 定义一个平移函数
def translate_coords(x, y, dx=dx, dy=dy):
    return (x + dx, y + dy)

# 读取原始SHP文件
gdf = gpd.read_file(input_shp_path)

# 确保原始数据是WGS84坐标系
if gdf.crs is None:
    gdf.crs = 'EPSG:4326'  # WGS84
elif gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs('EPSG:4326')

# 平移所有几何体
translated_geometries = []
for geom in gdf.geometry:
    # 使用shapely的transform函数应用坐标变换
    translated_geom = transform(translate_coords, geom)
    translated_geometries.append(translated_geom)

# 创建新的GeoDataFrame
gdf_translated = gpd.GeoDataFrame(gdf.drop(columns='geometry'), 
                                 geometry=translated_geometries, 
                                 crs='EPSG:4326')

# 保存为新的SHP文件
gdf_translated.to_file(output_shp_path, encoding='utf-8')

print(f"文件已成功保存到: {output_shp_path}")