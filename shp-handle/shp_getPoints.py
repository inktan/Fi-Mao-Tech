import geopandas as gpd
from shapely.geometry import Polygon
import geopandas as gpd
from shapely.geometry import LineString
import pandas as pd
from tqdm import tqdm

from geopy.distance import geodesic
from shapely.geometry import LineString, Point

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

import glob
import os

# 设置要搜索的文件夹路径
folder_path = r'F:\地学大数据\浙江省'  # 替换为你的文件夹路径

# 使用glob找到所有以.shp结尾的文件
shape_files = glob.glob(os.path.join(folder_path, '*.shp'))

# 打印出找到的文件的路径
for file_path in shape_files:
    print(file_path)
    if '嘉兴市' in file_path:
        continue
    if '丽水市' in file_path:
        continue
    if '台州市' in file_path:
        continue

    # shp_file_path = r'e:\work\sv_小丸\福田区面\深圳市.shp'
    shp_file_path = file_path
    gdf = gpd.read_file(shp_file_path)

    points_df = pd.DataFrame(columns=['id', 'longitude', 'latitude', 'name', 'type', 'oneway', 'bridge', 'tunnel' ])
    interval = 100
    print(gdf.shape)
    for index, row in tqdm(gdf.iterrows()):
        points = extract_points(row['geometry'],interval)
        # print(points)
        for point in points:
            points_df.loc[len(points_df)] = [index, point.x, point.y,row['name'],row['type'],row['oneway'],row['bridge'],row['tunnel'],]

    print(points_df)
    points_df.to_csv(shp_file_path.replace('.shp','_100m_.csv') , index=False)

