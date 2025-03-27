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

residential_land = gdf[gdf['Level2_cn'] == '居住用地']
business_land = gdf[gdf['Level2_cn'].isin(['商业服务用地', '商务办公用地','交通场站用地'])]
education_land = gdf[gdf['Level2_cn'] == '教育科研用地']
entertainment_land = gdf[gdf['Level2_cn'] == '公园与绿地用地']
public_service_land = gdf[gdf['Level2_cn'].isin([ '行政办公用地',  '医疗卫生用地', '体育与文化用地'])]
residential_land1 = residential_land.to_crs(epsg=3857)
business_land1 = business_land.to_crs(epsg=3857)
education_land1 = education_land.to_crs(epsg=3857)
entertainment_land1 = entertainment_land.to_crs(epsg=3857)
public_service_land1 = public_service_land.to_crs(epsg=3857)

residential_land1_data = residential_land1['geometry'].tolist()
business_land1_data = business_land1['geometry'].tolist()
education_land1_data = education_land1['geometry'].tolist()
entertainment_land1_data = entertainment_land1['geometry'].tolist()
public_service_land1_data = public_service_land1['geometry'].tolist()

csv_path = r'e:\work\sv_yueliang\备份小区名_lng_lat_01.csv'
# df1 = pd.read_csv(csv_path, encoding='gbk')
df1 = pd.read_csv(csv_path)
df1['lng_wgs84'] = pd.to_numeric(df1['lng_wgs84'], errors='coerce')
df1['lat_wgs84'] = pd.to_numeric(df1['lat_wgs84'], errors='coerce')
points = gpd.GeoDataFrame(df1, geometry=[Point(xy) for xy in zip(df1.lng_wgs84, df1.lat_wgs84)])
points.crs = {'init': 'epsg:4326'}

points_data1 = points.to_crs(epsg=3857)
points_data2 = points_data1['geometry'].tolist()

# 使用unary_union将所有的Polygon和MultiPolygon合并成一个几何图形
residential_land2_data = unary_union(residential_land1_data)
business_land2_data = unary_union(business_land1_data)
education_land2_data = unary_union(education_land1_data)
entertainment_land2_data = unary_union(entertainment_land1_data)
public_service_land2_data = unary_union(public_service_land1_data)

points_data1['land_use_mixed_score'] = 0

for i,point in enumerate(tqdm(points_data2)):
    # if i<75000:
    #     continue
    if point.is_empty:
        continue
    point = points_data2[i] 
    radius = 1500
    circle = point.buffer(radius)

    rate_dict={'residential_rate' : 0,
               'business_rate' :0,
               'education_rate': 0,
               'entertainment_rate' :0,
               'public_service_rate' :0}
    n = 5
    piln = 0
    # 计算落在圆内的几何图形的面积总和
    if circle.intersects(residential_land2_data):
        intersection_area = circle.intersection(residential_land2_data).area
        rate_dict['residential_rate'] = intersection_area/circle.area
        piln += rate_dict['residential_rate']*np.log(rate_dict['residential_rate'])

    if circle.intersects(business_land2_data):
        intersection_area = circle.intersection(business_land2_data).area
        rate_dict['business_rate'] = intersection_area/circle.area
        piln += rate_dict['business_rate']*np.log(rate_dict['business_rate'])

    if circle.intersects(education_land2_data):
        intersection_area = circle.intersection(education_land2_data).area
        rate_dict['education_rate'] = intersection_area/circle.area
        piln += rate_dict['education_rate']*np.log(rate_dict['education_rate'])

    if circle.intersects(entertainment_land2_data):
        intersection_area = circle.intersection(entertainment_land2_data).area
        rate_dict['entertainment_rate'] = intersection_area/circle.area
        piln += rate_dict['entertainment_rate']*np.log(rate_dict['entertainment_rate'])

    if circle.intersects(public_service_land2_data):
        intersection_area = circle.intersection(public_service_land2_data).area
        rate_dict['public_service_rate'] = intersection_area/circle.area
        piln += rate_dict['public_service_rate']*np.log(rate_dict['public_service_rate'])

    land_use_mixed_score = (-1)*piln/np.log(n)
    points_data1.at[i, 'land_use_mixed_score'] = land_use_mixed_score
    print(points_data1['land_use_mixed_score'][i])
    # print(points_data1['land_use_mixed_score'][i])
    # if i>10:
    #     break
    if i%1000 == 0:
        points_data1.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_land_use_mixed_score_01.csv', index=False)

points_data1.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_land_use_mixed_score_01.csv', index=False)


