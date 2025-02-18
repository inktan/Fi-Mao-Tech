
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
import csv

# 计算 透明率 垃圾箱密度

shp_paths = [
r'e:\work\sv_juanjuanmao\指标计算\ss_ashcan.shp',
]

# 3. 读取并合并所有 .shp 文件
gdfs = [gpd.read_file(shp) for shp in shp_paths]
point_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
print(point_gdf.crs)

# 读取所有带有名字的shp道路信息，读取点文件和线文件
line_file = r'e:\work\sv_juanjuanmao\澳门特别行政区_矢量路网01\道路_name.shp'
line_gdf = gpd.read_file(line_file)
print(line_gdf.crs)

# 确保点文件和线文件的坐标系一致
point_gdf = point_gdf.to_crs(line_gdf.crs)

cal_indicators = r'E:\work\sv_juanjuanmao\指标计算\垃圾箱密度.csv'
with open('%s'%cal_indicators ,'w' ,newline='') as f: 
    writer = csv.writer(f)
    writer.writerow(['index','Name','交通poi数量','街道长度','垃圾箱密度'])

# 遍历线文件，计算每个线段的几何信息
for index, line in line_gdf.iterrows():
    # 获取当前线段的几何信息
    line_geom = line.geometry
    line_length = line_geom.length

    # print(line)
    # break
    # print(line_geom)
    # print(line_length)
    
    # 找到距离线段小于20米的所有点
    nearby_points = point_gdf[point_gdf.geometry.distance(line_geom) < 20]
    # 计算这些点的数量
    point_count = len(nearby_points)
    # 检查 'wind' 列是否存在
    if 'ashcan;trash;can;garbage;can;wastebin;ash;bin;ash-bin;ashbin;dustbin;trash;barrel;trash;bin' in nearby_points.columns:
        # 统计 'wind' 列中的数字之和
        wind_sum = nearby_points['ashcan;trash;can;garbage;can;wastebin;ash;bin;ash-bin;ashbin;dustbin;trash;barrel;trash;bin'].sum()
        
    else:
        wind_sum = 0

    ratio = wind_sum / line_length

    rate_list = [index,line['Name'],point_count,line_length,ratio]

    with open('%s' % cal_indicators ,'a' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(rate_list)

    # 打印结果
    # print(f"Line {index}: Points within 20m: {point_count}, Length: {line_length:.2f}m, Ratio: {ratio:.4f}")
    # break

