
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
import csv

# 计算交通服务便捷率
# shp_paths = [
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_交通设施服务_20220103_145744.shp',
# ]

# 计算商业服务便捷率
# shp_paths = [
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_餐饮服务_20220103_145738.shp',
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_购物服务_20220103_145740.shp',
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_金融保险服务_20220103_145744.shp',
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_摩托车服务_20220103_145738.shp',
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_汽车服务_20220103_145737.shp',
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_汽车维修_20220103_145737.shp',
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_汽车销售_20220103_145737.shp',
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_生活服务_20220103_145740.shp',
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_体育休闲服务_20220103_145741.shp',
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\澳门特别行政区_医疗保健服务_20220103_145741.shp',
# ]

# 店铺密度
shp_paths = [
r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\merged_output_店铺.shp',
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

cal_indicators = r'E:\work\sv_juanjuanmao\指标计算\店铺密度.csv'
with open('%s'%cal_indicators ,'w' ,newline='') as f: 
    writer = csv.writer(f)
    writer.writerow(['index','Name','交通poi数量','街道长度','店铺密度'])

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
    # if point_count >0:
    #     print(point_count)
    #     print(nearby_points)
    # break

    # 计算点的数量与线段长度的比值
    ratio = point_count / line_length

    rate_list = [index,line['Name'],point_count,line_length,ratio]

    with open('%s' % cal_indicators ,'a' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(rate_list)

    # 打印结果
    # print(f"Line {index}: Points within 20m: {point_count}, Length: {line_length:.2f}m, Ratio: {ratio:.4f}")
    # break


