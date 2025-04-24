import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
import numpy as np

def process_shapefiles(point_shp_path, line_shp_path, output_path, buffer_distance=10):
    """
    处理点线SHP文件，将附近点的属性赋给线
    
    参数:
        point_shp_path: 点SHP文件路径
        line_shp_path: 线SHP文件路径
        output_path: 输出SHP文件路径
        buffer_distance: 搜索半径(米)
    """
    # 1. 读取SHP文件
    try:
        points_gdf = gpd.read_file(point_shp_path)
        lines_gdf = gpd.read_file(line_shp_path)
    except Exception as e:
        print(f"读取SHP文件失败: {e}")
        return

    # 2. 检查坐标系是否一致，如果不一致则转换
    if points_gdf.crs != lines_gdf.crs:
        print("警告: 点和线图层使用不同的坐标系，将点图层转换为线图层的坐标系")
        points_gdf = points_gdf.to_crs(lines_gdf.crs)
    
    # 3. 检查必需的字段是否存在
    required_fields = ['complexity', 'harmony']
    for field in required_fields:
        if field not in points_gdf.columns:
            print(f"错误: 点图层缺少必需的字段 '{field}'")
            return

    # 4. 为每条线创建缓冲区并查找附近的点
    lines_gdf['nearby_points_count'] = 0
    lines_gdf['avg_complexity'] = np.nan
    lines_gdf['avg_harmony'] = np.nan
    
    # 确保使用投影坐标系(以米为单位)进行距离计算
    if not lines_gdf.crs.is_projected:
        print("警告: 图层使用地理坐标系(度)，将临时转换为UTM进行计算")
        # 找到合适的UTM区域
        from pyproj import CRS
        from shapely.geometry import box
        bounds = lines_gdf.total_bounds
        centroid = box(*bounds).centroid
        utm_zone = int(np.floor((centroid.x + 180) / 6) + 1)
        utm_crs = CRS.from_dict({
            'proj': 'utm',
            'zone': utm_zone,
            'ellps': 'WGS84',
            'units': 'm',
            'south': centroid.y < 0
        })
        lines_proj = lines_gdf.to_crs(utm_crs)
        points_proj = points_gdf.to_crs(utm_crs)
    else:
        lines_proj = lines_gdf
        points_proj = points_gdf
    
    # 构建空间索引加速查询
    from rtree import index
    idx = index.Index()
    for i, point in points_proj.iterrows():
        idx.insert(i, point.geometry.bounds)
    
    # 5. 处理每条线
    for i, line in lines_proj.iterrows():
        # 创建缓冲区
        buffer = line.geometry.buffer(buffer_distance)
        
        # 使用空间索引查找可能附近的点
        possible_matches = list(idx.intersection(buffer.bounds))
        nearby_points = []
        
        for j in possible_matches:
            point = points_proj.iloc[j]
            if buffer.intersects(point.geometry):
                distance = line.geometry.distance(point.geometry)
                if distance <= buffer_distance:
                    nearby_points.append(point)
        
        # 如果有附近的点，计算平均值
        if nearby_points:
            avg_complexity = np.mean([p['complexity'] for p in nearby_points if not np.isnan(p['complexity'])])
            avg_harmony = np.mean([p['harmony'] for p in nearby_points if not np.isnan(p['harmony'])])
            
            lines_gdf.at[i, 'nearby_points_count'] = len(nearby_points)
            lines_gdf.at[i, 'avg_complexity'] = avg_complexity
            lines_gdf.at[i, 'avg_harmony'] = avg_harmony
    
    # 6. 保存结果
    try:
        lines_gdf.to_file(output_path, encoding='utf-8')
        print(f"处理完成，结果已保存到: {output_path}")
    except Exception as e:
        print(f"保存结果失败: {e}")

# 使用示例
if __name__ == "__main__":
    # 替换为你的实际文件路径
    point_shp = r"e:\work\sv_jumaorizhi\xc_src_complexity_harmony.shp"
    line_shp = r"e:\work\sv_jumaorizhi\road_merge.shp"
    output_shp = r"e:\work\sv_jumaorizhi\road_merge_value.shp"
    
    process_shapefiles(point_shp, line_shp, output_shp, buffer_distance=10)