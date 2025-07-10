import geopandas as gpd
from shapely.geometry import Point
import numpy as np

# 1. 读取shapefile文件
shapefile_path = r"e:\work\sv_xiufenganning\地理数据\Export_Output_wgs84.shp"
gdf = gpd.read_file(shapefile_path)

# 2. 准备存储所有网格点的列表
all_grid_points = []

# 3. 定义网格参数
grid_size = 9  # 9x9网格
distance = 50  # 50米间距

# 4. 处理每个原始点
for idx, row in gdf.iterrows():
    # 获取当前点的几何信息
    point = row.geometry
    if not isinstance(point, Point):
        # 如果不是点数据，则获取几何图形的代表性点
        point = point.representative_point()
    
    # 获取该点的经纬度坐标
    lon, lat = point.x, point.y
    
    # 计算偏移量（将米转换为经纬度）
    meters_per_degree_lat = 111320
    meters_per_degree_lon = 111320 * np.cos(np.radians(lat))
    
    # 计算50米对应的经纬度变化
    delta_lat = distance / meters_per_degree_lat
    delta_lon = distance / meters_per_degree_lon
    
    # 生成网格点
    for i in range(grid_size):
        for j in range(grid_size):
            # 计算当前点的经纬度
            current_lon = lon + (j - (grid_size-1)/2) * delta_lon
            current_lat = lat + (i - (grid_size-1)/2) * delta_lat
            
            # 创建新点并保留原始属性
            new_point = {
                'geometry': Point(current_lon, current_lat),
                'no': row['no'],  # 假设原始属性字段名为'no'
                '地点': row['地点'],  # 假设原始属性字段名为'地点'
                '地址': row['地址'],  # 假设原始属性字段名为'地址'
                'origin_id': idx  # 添加原始点ID用于追踪
            }
            all_grid_points.append(new_point)

# 5. 创建新的GeoDataFrame
grid_gdf = gpd.GeoDataFrame(all_grid_points, crs="EPSG:4326")  # WGS84

# 6. 保存结果
output_path = r"e:\work\sv_xiufenganning\地理数据\grid_points_with_attributes.shp"
grid_gdf.to_file(output_path)

print(f"成功生成网格点阵，共{len(grid_gdf)}个点，已保存到: {output_path}")