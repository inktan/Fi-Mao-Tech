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

# pm2.5 point
shapefile_path = r'f:\立方数据\2000-2023年全国1km分辨率的逐年PM2.5栅格数据\全国范围的数据\tif格式的数据\数据\2023_.shp'
gdf = gpd.read_file(shapefile_path)

# 点
csv_path = r'e:\work\sv_yueliang\备份小区名_lng_lat_01.csv'
# df1 = pd.read_csv(csv_path, encoding='gbk')
df1 = pd.read_csv(csv_path)
df1['lng_wgs84'] = pd.to_numeric(df1['lng_wgs84'], errors='coerce')
df1['lat_wgs84'] = pd.to_numeric(df1['lat_wgs84'], errors='coerce')
points = gpd.GeoDataFrame(df1, geometry=[Point(xy) for xy in zip(df1.lng_wgs84, df1.lat_wgs84)])
points.crs = {'init': 'epsg:4326'}

radius = 1500

# 重新投影到EPSG:3857
gdf = gdf.to_crs(epsg=3857)

point_data1 = points.to_crs(epsg=3857)
point_data2 = point_data1['geometry'].tolist()
point_data1['pm2.5'] = 0

for i,point in enumerate(tqdm(point_data2)):
    if point.is_empty:
        point_data1.at[i, 'pm2.5'] = 0
        continue

    circle = point.buffer(radius)
    # 判断每个点是否在圆内，并计算GDP总和
    pm25_sum = gdf[gdf['geometry'].within(circle)]['gdp_value'].sum()
    pm25_count = gdf[gdf['geometry'].within(circle)]['gdp_value'].count()
    print(pm25_sum, pm25_count)
    point_data1.at[i, 'pm2.5'] = pm25_sum / pm25_count
    # break

# pm2.5
# 优
# 0~35μg/m³

point_data1.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_pm2.5.csv', index=False)