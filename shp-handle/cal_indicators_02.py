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
for root, dirs, files in os.walk(r'E:\work\sv_juanjuanmao\澳门POI2022\ShapeFile2'):
    for file in files:
        if file.endswith(accepted_formats) and file.startswith('澳门特别行政区_'):
            roots.append(root)
            shp_names.append(file)
            file_path = os.path.join(root, file)
            shp_paths.append(file_path)

# shp_paths =[r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\merged_output_店铺.shp']

# 读取所有带有名字的shp道路信息，读取点文件和线文件
line_file = r'e:\work\sv_juanjuanmao\澳门特别行政区_矢量路网01\道路_name.shp'
line_gdf = gpd.read_file(line_file)

for index,shp_path in enumerate(tqdm(shp_paths)):
    print(index)
    print(shp_path)
    print(shp_names[index])
    
    cal_indicators = f'E:\work\sv_juanjuanmao\指标计算\{shp_names[index]}poi数量.csv'
    with open('%s'%cal_indicators ,'w' ,newline='') as f: 
        writer = csv.writer(f)
        writer.writerow(['index','Name',f'{shp_names[index]}poi数量'])

    # gdf = gpd.read_file(shp_path, encoding='GBK')
    gdf = gpd.read_file(shp_path)
    print(shp_path,gdf.shape)
    

    point_gdf = gpd.read_file(shp_path)
    print(point_gdf.crs)
    
    # 确保点文件和线文件的坐标系一致
    point_gdf = point_gdf.to_crs(line_gdf.crs)

    # 遍历线文件，计算每个线段的几何信息
    for index, line in line_gdf.iterrows():
        # 获取当前线段的几何信息
        line_geom = line.geometry

        # 找到距离线段小于20米的所有点
        nearby_points = point_gdf[point_gdf.geometry.distance(line_geom) < 20]
        # 计算这些点的数量
        point_count = len(nearby_points)

        rate_list = [index,line['Name'],point_count]

        with open('%s' % cal_indicators ,'a' ,newline='') as f:
            writer = csv.writer(f)
            writer.writerow(rate_list)


