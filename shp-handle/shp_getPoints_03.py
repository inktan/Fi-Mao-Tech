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


# folder_path = r'F:\立方数据\2025年道路数据\【立方数据学社】武汉市'  # 替换为你的文件夹路径
# shape_files = glob.glob(os.path.join(folder_path, '*.shp'))

shape_files=[
    r'e:\work\sv_momo\sv_20250512\street_network.shp',
]

for file_path in shape_files:
    print(file_path)

    # shp_file_path = r'e:\work\sv_小丸\福田区面\深圳市.shp'
    shp_file_path = file_path
    gdf = gpd.read_file(shp_file_path)
    # gdf = gpd.read_file(shp_file_path, encoding='latin1')
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)  # 设置原始 CRS
    gdf = gdf.to_crs(epsg=4326)  # 转换为WGS 84

    # points_df = pd.DataFrame(columns=['id', 'longitude', 'latitude', 'name', 'type', 'oneway', 'bridge', 'tunnel' ])
    # points_df = pd.DataFrame(columns=['id','osm_id', 'longitude', 'latitude', 'name_2'])
    points_df = pd.DataFrame(columns=['id', 'longitude', 'latitude'])
    interval = 50
    print(gdf.shape)

    # gdf['name_2'] = gdf['name_2'].str.encode('latin1').str.decode('utf-8')  # 尝试 latin1 → gbk

    for index, row in tqdm(gdf.iterrows()):
        geometry = row['geometry']
        if geometry is None:
            continue

        if geometry.geom_type == 'Polygon':
            # 提取多边形的边线
            exterior = geometry.exterior
            points = extract_points(LineString(exterior.coords),interval)
            for point in points:
                points_df.loc[len(points_df)] = [index,  point.x, point.y]
        elif geometry.geom_type == 'MultiPolygon':
            for polygon in geometry.geoms:
                exterior = polygon.exterior
                points = extract_points(LineString(exterior.coords),interval)
                for point in points:
                    points_df.loc[len(points_df)] = [index,  point.x, point.y]
        # print(geometry)
        # print(geometry.geom_type)

        if geometry.geom_type == 'MultiLineString':
            print(geometry.geom_type)
            for line in geometry.geoms:
                points = extract_points(line,interval)
                for point in points:
                    points_df.loc[len(points_df)] = [index, point.x, point.y]
        elif geometry.geom_type == 'LineString':
            points = extract_points(geometry,interval)
            for point in points:
                points_df.loc[len(points_df)] = [index,  point.x, point.y]
        elif  geometry.geom_type == 'Point':
                point = Point(geometry.coords[0])
                points_df.loc[len(points_df)] = [index, point.x, point.y]

    print(points_df)

    unique_count = points_df.shape[0]
    print(f'原数据有 {points_df.shape} 行数据')
    points_df.to_csv(shp_file_path.replace('.shp',f'_{interval}m_.csv') , index=False)
    # 如果 result_gdf 是 DataFrame，则将其转换为 GeoDataFrame
    if type(points_df) == pd.core.frame.DataFrame:
        points_df = gpd.GeoDataFrame(points_df, geometry=gpd.points_from_xy(points_df.longitude, points_df.latitude, crs='EPSG:4326'))

    points_df.to_file(shp_file_path.replace('.shp',f'_{interval}m_.shp') , index=False)

    points_df = points_df.drop_duplicates(subset=['longitude', 'latitude'])
    # df_unique = points_df.drop_duplicates(subset=['id'])
    # 打印去重后的数据行数
    print(f'去重后共有 {points_df.shape} 行数据')

    points_df.to_csv(shp_file_path.replace('.shp',f'_{interval}m_unique.csv') , index=False)
    # 检查 result_gdf 的类型
    print(type(points_df))
    # 如果 result_gdf 是 DataFrame，则将其转换为 GeoDataFrame
    if type(points_df) == pd.core.frame.DataFrame:
        points_df = gpd.GeoDataFrame(points_df, geometry=gpd.points_from_xy(points_df.longitude, points_df.latitude, crs='EPSG:4326'))
    points_df.to_file(shp_file_path.replace('.shp',f'_{interval}m_unique.shp') , index=False)
    
    # 3. 使用KDTree进行高效空间查询
    print("构建空间索引...")
    coords = np.array([(geom.x, geom.y) for geom in points_df.geometry])
    tree = cKDTree(coords)
    
    # 4. 找出需要删除的点
    print("查找邻近点...")
    to_remove = set()

    min_dist = -0.1
    max_dist = interval
        
    # 使用批量查询提高性能
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
                if min_dist < dist < max_dist:
                    # 删除其中一个点(这里选择删除索引较大的)
                    to_remove.add(j)
    
    # 5. 创建过滤后的GeoDataFrame
    print("创建结果数据集...")
    mask = [i not in to_remove for i in range(len(points_df))]
    points_df = points_df[mask]
    
    points_df.to_csv(shp_file_path.replace('.shp',f'_{interval}m_unique_Spatial_Balance.csv') , index=False)
    # 检查 result_gdf 的类型
    print(type(points_df))
    # 如果 result_gdf 是 DataFrame，则将其转换为 GeoDataFrame
    if type(points_df) == pd.core.frame.DataFrame:
        points_df = gpd.GeoDataFrame(points_df, geometry=gpd.points_from_xy(points_df.longitude, points_df.latitude, crs='EPSG:4326'))
    points_df.to_file(shp_file_path.replace('.shp',f'_{interval}m_unique_Spatial_Balance.shp') , index=False)







