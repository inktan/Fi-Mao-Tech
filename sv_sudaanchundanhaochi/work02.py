import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

# 设置输入和输出路径
input_shp_path = r"e:\work\苏大-鹌鹑蛋好吃\热力图\merged_output_100.csv"
output_shp_path = r"e:\work\苏大-鹌鹑蛋好吃\gis数据-wgs84_01\merged_output_100\merged_output_100.shp"

# 读取CSV文件
df = pd.read_csv(input_shp_path)  # 替换为你的文件路径

# 假设原始坐标系是UTM（根据坐标值判断），需要指定UTM区域
# 从y坐标(347xxxx)判断可能在北半球，假设是UTM zone 50N(32650)
# 请根据实际数据来源确认正确的UTM区域
utm_zone = '32650'  # 这里使用UTM zone 50N (WGS84)作为示例

# 创建GeoDataFrame，将x,y转换为点几何
geometry = [Point(xy) for xy in zip(df['x'], df['y'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=f'EPSG:{utm_zone}')

# 转换为WGS84坐标系 (EPSG:4326)
gdf_wgs84 = gdf.to_crs(epsg=4326)


# 确保输出目录存在
output_dir = os.path.dirname(output_shp_path)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 保存修正后的SHP文件
gdf.to_file(output_shp_path)
