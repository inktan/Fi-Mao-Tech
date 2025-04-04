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
shapefile_path = r'e:\work\sv_gonhoo\标签分类.csv'
df = gpd.read_file(shapefile_path)
# print(df.head())
# print(df.columns)
# 分类项列

# 住宿服务Accommodation
# 餐饮服务（Food & Beverage）
# 旅游景点（Tourist Attractions）
# 生活服务（Living Services）
# 零售购物（Retail & Shopping）
# 交通设施（Transportation Facilities）
# 休闲娱乐（Entertainment）
# 公共服务（Public Services）
# 文化设施（Cultural facilities）
# 教育机构（Educational institutions）

dst_crs = 'EPSG:4326'
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.place_lon, df.place_lat), crs=dst_crs)
# 保存为Shapefile
# gdf.to_file(r'e:\work\sv_shushu\澳门特别行政区_矢量路网\道路_15m_unique_01.shp', driver='ESRI Shapefile')
# print(gdf.head())
# print(gdf.columns)

gdf = gdf[gdf['分类项'].str.contains('住宿服务|餐饮服务|旅游景点|生活服务|零售购物|交通设施|休闲娱乐|公共服务|文化设施|教育机构', case=False)]

# 筛选条件：分类项列不包含'旅游'且不包含'教育'
# gdf = gdf[~gdf['分类项'].str.contains('旅游') & ~gdf['分类项'].str.contains('教育')]

# print(gdf.head())
# print(gdf.columns)
# raise ValueError("===========================>")

# 点
# Longitude	Latitude

csv_path = r'e:\work\sv_gonhoo\0-Zvalue-Totle-fukuoka-city.csv'
# df1 = pd.read_csv(csv_path, encoding='gbk')
df1 = pd.read_csv(csv_path)
df1['Longitude'] = pd.to_numeric(df1['Longitude'], errors='coerce')
df1['Latitude'] = pd.to_numeric(df1['Latitude'], errors='coerce')
points = gpd.GeoDataFrame(df1, geometry=[Point(xy) for xy in zip(df1.Longitude, df1.Latitude)])
points.crs = {'init': 'epsg:4326'}

radius = 1500

# 重新投影到EPSG:3857
gdf = gdf.to_crs(epsg=3857)

point_data1 = points.to_crs(epsg=3857)
point_data2 = point_data1['geometry'].tolist()
point_data1['服务设施密度'] = 0

for i,point in enumerate(tqdm(point_data2)):
    # if i>20:
    #     break
    if point.is_empty:
        point_data1.at[i, '服务设施密度'] = 0
        continue

    circle = point.buffer(radius)
    _count = gdf[gdf['geometry'].within(circle)]['geometry'].count()
    print(_count)
    point_data1.at[i, '服务设施密度'] = _count/circle.area

    # break

point_data1.to_csv(r'e:\work\sv_gonhoo\0-Zvalue-Totle-fukuoka-city02.csv', index=False)