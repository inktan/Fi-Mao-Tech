from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
from tqdm import tqdm

from geopy.distance import geodesic
from shapely.geometry import LineString, Point, Polygon
import glob
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


folder_path = r'f:\立方数据\2025年道路数据\【立方数据学社】澳门特别行政区'  # 替换为你的文件夹路径
shape_files = glob.glob(os.path.join(folder_path, '*.shp'))

shape_files=[r'f:\立方数据\2025年道路数据\【立方数据学社】西安市\西安市.shp']

for file_path in shape_files:
    print(file_path)

    # shp_file_path = r'e:\work\sv_小丸\福田区面\深圳市.shp'
    shp_file_path = file_path
    gdf = gpd.read_file(shp_file_path)
    # gdf = gdf.to_crs(epsg=4326)  # 转换为WGS 84

    points_df = pd.DataFrame(columns=['id', 'longitude', 'latitude', 'name', 'type', 'oneway', 'bridge', 'tunnel' ])
    interval = 50
    print(gdf.shape)
    for index, row in tqdm(gdf.iterrows()):

        geometry = row['geometry']
        if geometry is None:
            continue

        if geometry.geom_type == 'Polygon':
            # 提取多边形的边线
            exterior = geometry.exterior
            points = extract_points(LineString(exterior.coords),interval)
            for point in points:
                points_df.loc[len(points_df)] = [index, point.x, point.y,row['name'],row['type'],row['oneway'],row['bridge'],row['tunnel'],]
        elif geometry.geom_type == 'MultiPolygon':
            for polygon in geometry.geoms:
                exterior = polygon.exterior
                points = extract_points(LineString(exterior.coords),interval)
                for point in points:
                    points_df.loc[len(points_df)] = [index, point.x, point.y,row['name'],row['type'],row['oneway'],row['bridge'],row['tunnel'],]
        # print(geometry)
        # print(geometry.geom_type)

        if geometry.geom_type == 'MultiLineString':
            print(geometry.geom_type)
            for line in geometry.geoms:
                points = extract_points(line,interval)
                for point in points:
                    points_df.loc[len(points_df)] = [index, point.x, point.y,row['name'],row['type'],row['oneway'],row['bridge'],row['tunnel'],]
        elif geometry.geom_type == 'LineString':
            points = extract_points(geometry,interval)
            for point in points:
                points_df.loc[len(points_df)] = [index, point.x, point.y,row['name'],row['type'],row['oneway'],row['bridge'],row['tunnel'],]
        elif  geometry.geom_type == 'Point':
                point = Point(geometry.coords[0])
                points_df.loc[len(points_df)] = [index, point.x, point.y,row['name'],row['type'],row['oneway'],row['bridge'],row['tunnel'],]

    print(points_df)
    points_df.to_csv(shp_file_path.replace('.shp','_15m_.csv') , index=False)

