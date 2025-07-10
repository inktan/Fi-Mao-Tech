import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np

# 输入文件路径
file_path = r"e:\work\sv_xiufenganning\地理数据\Export_Output_wgs84.shp"
# 输出文件路径
output_path = r"e:\work\sv_xiufenganning\地理数据\circles_500m.shp"

# 读取SHP文件
gdf = gpd.read_file(file_path)

# 确保数据是点要素
if not all(gdf.geometry.type == 'Point'):
    raise ValueError("输入SHP文件必须只包含点要素")

# 定义创建圆的函数
def create_circle(center_point, radius_meters, num_points=36):
    """
    根据中心点和半径(米)创建一个圆形多边形
    
    参数:
        center_point: shapely Point对象
        radius_meters: 圆的半径(米)
        num_points: 用于近似圆的点数(默认36)
    
    返回:
        shapely Polygon对象
    """
    # 将米转换为度(近似转换，适用于小范围)
    # 地球半径约6378137米
    # 1度 ≈ 111.32 km (纬度方向)
    radius_deg = radius_meters / 111320
    
    angles = np.linspace(0, 360, num_points)
    points = []
    for angle in angles:
        # 计算圆上的点
        x = center_point.x + radius_deg * np.cos(np.radians(angle))
        y = center_point.y + radius_deg * np.sin(np.radians(angle))
        points.append((x, y))
    
    return Polygon(points)

# 为每个点创建500米直径的圆(半径250米)
gdf['geometry'] = gdf.geometry.apply(lambda p: create_circle(p, 250))

# 保存结果到新的SHP文件
gdf.to_file(output_path)

print(f"成功生成500米直径圆形并保存到: {output_path}")