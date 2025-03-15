import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
import csv

# 计算 透明率 垃圾箱密度 绿化率 
shp_paths = [
r'e:\work\sv_juanjuanmao\指标计算\window_ss.shp',
]

gdfs = [gpd.read_file(shp) for shp in shp_paths]
point_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
print(point_gdf.crs)

for filename in os.listdir(r'E:\work\sv_juanjuanmao\20250308\八条路线'):
    if filename.endswith(".shp"):
        file_path = os.path.join(r'E:\work\sv_juanjuanmao\20250308\八条路线', filename)
        line_gdf = gpd.read_file(file_path)
        # print(line_gdf.crs)

        point_gdf = point_gdf.to_crs(line_gdf.crs)

        point_gdf = point_gdf.to_crs(epsg=32633)
        line_gdf = line_gdf.to_crs(epsg=32633)

        for index, line in line_gdf.iterrows():
            line_geom = line.geometry
            line_length = line_geom.length

            # print(line_length)
            # 距离线段小于20米的所有点
            nearby_points = point_gdf[point_gdf.geometry.distance(line_geom) < 20]
            point_count = len(nearby_points)
            # if point_count >0:
            #     print(line_length,point_count)

            # 检查 'wind' 列是否存在
            if 'windowpane' in nearby_points.columns:
                # 统计 'wind' 列中的数字之和
                wind_sum = nearby_points['windowpane'].sum()
                
            else:
                wind_sum = 0

            print(line_length,wind_sum)
