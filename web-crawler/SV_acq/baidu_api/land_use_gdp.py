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

# gdp 点数据
shapefile_path = r'f:\立方数据\2014-2020年GDP栅格数据（全国分省分市无需转发）\按城市裁剪的数据\【立方数据学社】上海市\China_GDP_2020_.shp'
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

point_data1['gdp'] = 0

for i,point in enumerate(tqdm(point_data2)):
    if point.is_empty:
        point_data1.at[i, 'gdp'] = 0
        continue

    circle = point.buffer(radius)
    # 判断每个点是否在圆内，并计算GDP总和
    gdp_sum = gdf[gdf['geometry'].within(circle)]['gdp_value'].sum()
    point_data1.at[i, 'gdp'] = gdp_sum
    # break

point_data1.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_gdp.csv', index=False)




