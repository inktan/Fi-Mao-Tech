import geopandas as gpd
from shapely.geometry import Polygon

from tqdm import tqdm
import os
import pandas as pd
from shapely.geometry import Point, LineString
import csv

roots = []
shp_names = []
shp_paths = []
accepted_formats = (".shp")
for root, dirs, files in os.walk(r'E:\work\sv_juanjuanmao\澳门POI2022\ShapeFile'):
    for file in files:
        if file.endswith(accepted_formats) and file.startswith('澳门特别行政区_'):
            roots.append(root)
            shp_names.append(file)
            file_path = os.path.join(root, file)
            shp_paths.append(file_path)

# 计算功能混合度
for index,shp_path in enumerate(tqdm(shp_paths)):

    point_gdf = gpd.read_file(shp_path)
    point_gdf = point_gdf.to_crs(epsg=32633)

    cal_indicators = f'E:\work\sv_juanjuanmao\\20250308\八条路线\指标计算\{shp_names[index]}poi数量.csv'
    with open('%s'%cal_indicators ,'w' ,newline='') as f: 
        writer = csv.writer(f)
        writer.writerow(['Name',f'{shp_names[index]}poi数量'])

    for filename in os.listdir(r'E:\work\sv_juanjuanmao\20250308\八条路线'):
        if filename.endswith(".shp"):
            file_path = os.path.join(r'E:\work\sv_juanjuanmao\20250308\八条路线', filename)
            line_gdf = gpd.read_file(file_path)
            # print(line_gdf.crs)

            line_gdf = line_gdf.to_crs(epsg=32633)

            # 遍历线文件，计算每个线段的几何信息
            for index, line in line_gdf.iterrows():
                # 获取当前线段的几何信息
                line_geom = line.geometry

                # 找到距离线段小于20米的所有点
                nearby_points = point_gdf[point_gdf.geometry.distance(line_geom) < 20]
                # 计算这些点的数量
                point_count = len(nearby_points)

                rate_list = [file_path,point_count]

                with open('%s' % cal_indicators ,'a' ,newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(rate_list)


