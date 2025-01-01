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

shapefile_path = r'f:\shanghaijiaoda_poi_shp\shanghai_build\shanghai_build.shp'
gdf = gpd.read_file(shapefile_path)

arch_buildings = gdf.to_crs(epsg=3857)

arch_buildings_data = arch_buildings['geometry'].tolist()

csv_path = r'e:\work\sv_yueliang\备份小区名_lng_lat_01.csv'
df1 = pd.read_csv(csv_path, encoding='gbk')
df1['lng_wgs84'] = pd.to_numeric(df1['lng_wgs84'], errors='coerce')
df1['lat_wgs84'] = pd.to_numeric(df1['lat_wgs84'], errors='coerce')
points = gpd.GeoDataFrame(df1, geometry=[Point(xy) for xy in zip(df1.lng_wgs84, df1.lat_wgs84)])
points.crs = {'init': 'epsg:4326'}

points_data1 = points.to_crs(epsg=3857)
points_data2 = points_data1['geometry'].tolist()

points_data1['land_use_average_height'] = 0

for i,point in enumerate(tqdm(points_data2)):
    # if i<-1:
    #     continue
    # if i>=10000:
    #     continue
    if point.is_empty:
        continue
    point = points_data2[i]
    radius = 1500
    circle = point.buffer(radius)

    intersecting = arch_buildings[arch_buildings.geometry.intersects(circle)]
    intersecting_buildings = intersecting['height'].tolist()
    
    if len(intersecting_buildings)>0:
        points_data1.at[i, 'land_use_average_height'] =  sum(intersecting_buildings) / len(intersecting_buildings)
    else:
        points_data1.at[i, 'land_use_average_height'] = 0
        
    print(points_data1['land_use_average_height'][i])
    # print(points_data1['land_use_mixed_score'][i])
    # if i>10:
    #     break
    if i%1000 == 0:
        points_data1.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_land_use_average_height_01.csv', index=False)

points_data1.to_csv(r'e:\work\sv_yueliang\备份小区名_lng_lat_land_use_average_height_01.csv', index=False)


