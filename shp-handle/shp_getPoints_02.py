from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
import numpy as np

from geopy.distance import geodesic
from shapely.geometry import LineString, Point, Polygon
import glob
from scipy.spatial import cKDTree
import pyproj

import os

def extract_points(line, interval):
    # total_length = sum(geodesic((line.coords[i][1], line.coords[i][0]), (line.coords[i + 1][1], line.coords[i + 1][0])).meters for i in range(len(line.coords) - 1))
    points = [Point(line.coords[0])]

    # 遍历线段，按间隔取点
    for i in range(len(line.coords) - 1):
        start = (line.coords[i][1], line.coords[i][0])
        end = (line.coords[i + 1][1], line.coords[i + 1][0])
        segment_length = geodesic(start, end).meters
        
        current_distance = 0
        # while current_distance + interval <= segment_length:
        while True:
            if segment_length < interval:
                points.append(Point(end[1], end[0]))
                break
            # 计算在当前线段上的比例
            ratio = (current_distance + interval) / segment_length
            if ratio > 1:
                points.append(Point(end[1], end[0]))
                break
            
            # 计算新点的坐标
            new_y = start[0] + (end[0] - start[0]) * ratio
            new_x = start[1] + (end[1] - start[1]) * ratio
            points.append(Point(new_x, new_y))
            
            # 更新当前距离
            current_distance += interval
    return points

def process_geometry(row,interval):
    geometry = row['geometry']
    index = row.name  # 获取索引
    points = []
    
    if geometry is None:
        return points
        
    if geometry.geom_type == 'Polygon':
        exterior = geometry.exterior
        points.extend(extract_points(LineString(exterior.coords), interval))
    elif geometry.geom_type == 'MultiPolygon':
        for polygon in geometry.geoms:
            exterior = polygon.exterior
            points.extend(extract_points(LineString(exterior.coords), interval))
    elif geometry.geom_type == 'MultiLineString':
        for line in geometry.geoms:
            points.extend(extract_points(line, interval))
    elif geometry.geom_type == 'LineString':
        points.extend(extract_points(geometry, interval))
    elif geometry.geom_type == 'Point':
        points.append(Point(geometry.coords[0]))
    
    return [(index, point.x, point.y) for point in points]

# folder_path = r'E:\work\sv_zhaolu\roads'  # 替换为你的文件夹路径
# shape_files = glob.glob(os.path.join(folder_path, '*.shp'))

shape_files=[
    r'f:\大数据\2025年8月份道路矢量数据\分城市的道路数据\澳门特别行政区-260208-free\gis_osm_roads_free_1.shp',
]

for file_path in shape_files:
    print(file_path)

    shp_file_path = file_path
    gdf = gpd.read_file(shp_file_path)
    # 读取后立即转换坐标系
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326") # 转换为地理坐标系
    
    # 应用函数并创建DataFrame
    interval = 50
    results = gdf.apply(process_geometry, axis=1, interval=interval).explode()
    points_df = pd.DataFrame(list(results), columns=['osm_id', 'longitude', 'latitude'])
    # points_df = points_df.drop(columns=['geometry'])

    print(points_df)

    unique_count = points_df.shape[0]
    print(f'原数据有 {points_df.shape} 行数据')
    # points_df.to_csv(shp_file_path.replace('.shp',f'_{interval}m_.csv') , index=False)
    # 如果 result_gdf 是 DataFrame，则将其转换为 GeoDataFrame
    if type(points_df) == pd.core.frame.DataFrame:
        points_df = gpd.GeoDataFrame(points_df, geometry=gpd.points_from_xy(points_df.longitude, points_df.latitude, crs='EPSG:4326'))

    # points_df.to_file(shp_file_path.replace('.shp',f'_{interval}m_.shp') , index=False)
    points_df = points_df.drop_duplicates(subset=['longitude', 'latitude'])
    # df_unique = points_df.drop_duplicates(subset=['id'])
    # 打印去重后的数据行数
    print(f'去重后共有 {points_df.shape} 行数据')
    # points_df = points_df.drop(columns=['geometry'])

    points_df.to_csv(shp_file_path.replace('.shp',f'_{interval}m_unique.csv') , index=False)
    # continue
    # raise('程序中断，检查数据')

    # 检查 result_gdf 的类型
    print(type(points_df))
    # 如果 result_gdf 是 DataFrame，则将其转换为 GeoDataFrame
    if type(points_df) == pd.core.frame.DataFrame:
        points_df = gpd.GeoDataFrame(points_df, geometry=gpd.points_from_xy(points_df.longitude, points_df.latitude, crs='EPSG:4326'))
    # points_df.to_file(shp_file_path.replace('.shp',f'_{interval}m_unique.shp') , index=False)

    gdf = points_df
    # 确保是WGS84 (EPSG:4326)坐标系
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')
    
    # 2. 将经纬度转换为平面坐标(UTM)以便精确计算距离
    print("坐标转换中...")
    centroid = gdf.geometry.unary_union.centroid if hasattr(gdf.geometry, 'unary_union') else gdf.geometry.union_all().centroid
    utm_zone = int(np.floor((centroid.x + 180) / 6) + 1)
    utm_crs = f'EPSG:{32600 + utm_zone}' if centroid.y >= 0 else f'EPSG:{32700 + utm_zone}'
    
    # 转换为UTM坐标
    gdf_utm = gdf.to_crs(utm_crs)
    
    # 3. 使用KDTree进行高效空间查询
    print("构建空间索引...")
    coords = np.array([(geom.x, geom.y) for geom in gdf_utm.geometry])
    tree = cKDTree(coords)
    
    # 4. 找出需要删除的点
    print("查找邻近点...")
    to_remove = set()
    
    # 使用批量查询提高性能
    max_dist = interval  # 最大距离阈值(米)
    batch_size = 1000  # 根据内存调整
    for i in tqdm(range(0, len(coords), batch_size), desc="处理进度"):
        batch_indices = range(i, min(i + batch_size, len(coords)))
        # 查询所有点对，距离在max_dist以内的
        neighbors = tree.query_ball_point(coords[batch_indices], r=max_dist, return_sorted=True)
        
        for idx, neighbors_list in zip(batch_indices, neighbors):
            # 跳过已经标记要删除的点
            if idx in to_remove:
                continue
                
            # 检查每个邻居
            for j in neighbors_list:
                if j <= idx:  # 避免重复检查
                    continue
                    
                dist = np.linalg.norm(coords[idx] - coords[j])
                if -0.1 < dist < max_dist:
                    # 删除其中一个点(这里选择删除索引较大的)
                    to_remove.add(j)
    
    # 5. 创建过滤后的GeoDataFrame
    print("创建结果数据集...")
    mask = [i not in to_remove for i in range(len(gdf))]
    filtered_gdf = gdf[mask]
    
    # 6. 保存结果
    print("保存结果...")
    filtered_gdf.to_file(shp_file_path.replace('.shp', f'_{interval}m_Spatial.shp') , index=False)

    filtered_gdf["index"] = range(len(filtered_gdf))  # 新增 0,1,2... 列
    filtered_gdf.drop(columns=['geometry']).to_csv(shp_file_path.replace('.shp', f'_{interval}m_Spatial.csv') , index=False)
    
    print(f"处理完成 - 原始点数: {len(gdf)}, 处理后点数: {len(filtered_gdf)}, 删除点数: {len(to_remove)}")

