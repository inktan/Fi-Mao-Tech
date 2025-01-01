import csv
import pandas as pd
import geopandas as gpd
import os
import requests 
from coordinate_converter import transCoordinateSystem, transBmap
from math import radians, cos, sin, asin, sqrt
import csv
from tqdm import tqdm

from shapely.geometry import MultiLineString, Point, Polygon
from shapely.ops import unary_union
import numpy as np

shapefile_path = r'f:\shanghaijiaoda_poi_shp\shanghai_shp\上海市.shp'
gdf = gpd.read_file(shapefile_path)

#住宅、商业、教育、娱乐和公共服务

# 对应关系
# 公共管理和服务用地 +++ 公园与绿地用地 行政办公用地 教育科研用地 医疗卫生用地 体育与文化用地
# 居住用地 +++ 居住用地 
# 工业用地 +++ 工业用地
# 交通用地 +++ 机场设施用地
# 商业用地 +++ 商业服务用地 商务办公用地 交通场站用地

entertainment_land = gdf[gdf['Level2_cn'] == '公园与绿地用地']
entertainment_land1 = entertainment_land.to_crs(epsg=3857)
entertainment_land1_data = entertainment_land1['geometry'].tolist()

csv_path = r'e:\work\sv_yueliang\备份小区名_lng_lat_01.csv'
df1 = pd.read_csv(csv_path, encoding='gbk')
df1['lng_wgs84'] = pd.to_numeric(df1['lng_wgs84'], errors='coerce')
df1['lat_wgs84'] = pd.to_numeric(df1['lat_wgs84'], errors='coerce')
points = gpd.GeoDataFrame(df1, geometry=[Point(xy) for xy in zip(df1.lng_wgs84, df1.lat_wgs84)])
points.crs = {'init': 'epsg:4326'}

points_data1 = points.to_crs(epsg=3857)
points_data2 = points_data1['geometry'].tolist()

# 使用unary_union将所有的Polygon和MultiPolygon合并成一个几何图形
entertainment_land2_data = unary_union(entertainment_land1_data)

points_data1['land_use_mixed_score'] = 0

for i,point in enumerate(tqdm(points_data2)):
    # if i<75000:
    #     continue
    if point.is_empty:
        continue
    point = points_data2[i] 
    radius = 1500
    circle = point.buffer(radius)

    # 计算落在圆内的几何图形的面积总和
    if circle.intersects(entertainment_land2_data):
        intersection_area = circle.intersection(entertainment_land2_data).area
        points_data1.at[i, 'green_rate'] = intersection_area/circle.area
    else:
        points_data1.at[i, 'green_rate'] = 0
    print(points_data1['green_rate'][i])

    # print(points_data1['land_use_mixed_score'][i])
    # if i>10:
    #     break
    if i%1000 == 0:
        points_data1.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_land_green_rate_01.csv', index=False)

points_data1.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_land_use_green_rate_01.csv', index=False)


