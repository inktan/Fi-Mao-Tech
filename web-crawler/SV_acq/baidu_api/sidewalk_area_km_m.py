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

# 线
shapefile_path = r'f:\shanghaijiaoda_poi_shp\shanghai_osm\shanghai_osm.shp'
gdf = gpd.read_file(shapefile_path)
column_name = 'fclass' 
# 提取人行相关的路
values_to_find = ['residential', 'footway', 'living_street']
filtered_data = gdf[gdf[column_name].isin(values_to_find)]

# 点
csv_path = r'f:\shanghaijiaoda_poi_shp\20240614\work03_address_lng_lat_01.csv'
df1 = pd.read_csv(csv_path)
df1['lng'] = pd.to_numeric(df1['lng'], errors='coerce')
df1['lat'] = pd.to_numeric(df1['lat'], errors='coerce')
gdf2 = gpd.GeoDataFrame(df1, geometry=[Point(xy) for xy in zip(df1.lng, df1.lat)])
gdf2.crs = {'init': 'epsg:4326'}

# 重新投影到EPSG:3857
filtered_road_data1 = filtered_data.to_crs(epsg=3857)
point_data1 = gdf2.to_crs(epsg=3857)

filtered_road_data2 = filtered_road_data1['geometry'].tolist()
point_data2 = point_data1['geometry'].tolist()

radius = 1500
point_data1['rate'] = 0

# 使用unary_union将所有道路数据合并为一个几何体
all_roads_union = unary_union(filtered_road_data2)

for i,point in enumerate(tqdm(point_data2)):
    if point.is_empty:
        point_data1.at[i, 'rate'] = 0
        continue

    circle = point.buffer(radius)
    intersection = circle.intersection(all_roads_union)
    total_length = intersection.length / 1000.0  # 转换为千米
    # 计算率值
    rate = total_length / circle.area
    point_data1.at[i, 'rate'] = rate
    
    # break
point_data1.to_csv(r'f:\shanghaijiaoda_poi_shp\20240614\work03_id_rate.csv', index=False)