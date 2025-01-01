import geopandas as gpd
from shapely.geometry import Polygon
import geopandas as gpd
from shapely.geometry import LineString
import pandas as pd
from tqdm import tqdm

from geopy.distance import geodesic
from shapely.geometry import LineString, Point

shp_file_path = r'h:\地学大数据\2024年5月全国路网数据\2024年5月全国路网数据_分省市\广东省\深圳市.shp'
gdf = gpd.read_file(shp_file_path)

def extract_points(line, interval):
    total_length = sum(geodesic((line.coords[i][1], line.coords[i][0]), (line.coords[i + 1][1], line.coords[i + 1][0])).meters for i in range(len(line.coords) - 1))
    points = [Point(line.coords[0])]

    current_distance = 0
    # 遍历线段，按间隔取点
    for i in range(len(line.coords) - 1):
        start = (line.coords[i][1], line.coords[i][0])
        end = (line.coords[i + 1][1], line.coords[i + 1][0])
        segment_length = geodesic(start, end).meters
        
        while current_distance + interval <= total_length:
            # 计算在当前线段上的比例
            ratio = (current_distance + interval) / segment_length
            if ratio > 1:
                break
            
            # 计算新点的坐标
            new_y = start[0] + (end[0] - start[0]) * ratio
            new_x = start[1] + (end[1] - start[1]) * ratio
            points.append(Point(new_x, new_y))
            
            # 更新当前距离
            current_distance += interval

    return points

points_df = pd.DataFrame(columns=['id', 'longitude', 'latitude'])
interval = 40
print(gdf.shape)
for index, row in tqdm(gdf.iterrows()):
    points = extract_points(row['geometry'],interval)
    # print(points)
    for point in points:
        points_df.loc[len(points_df)] = [index, point.x, point.y]

print(points_df)
points_df.to_csv(r'h:\地学大数据\2024年5月全国路网数据\2024年5月全国路网数据_分省市\广东省\深圳市.csv', index=False)

