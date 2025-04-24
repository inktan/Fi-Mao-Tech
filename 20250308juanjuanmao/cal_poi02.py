
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

# 开放社交场所密度
shp_paths = [
r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\merged_output_开放设计场所.shp',
]

# 店铺密度
# shp_paths = [
# r'e:\work\sv_juanjuanmao\澳门POI2022\ShapeFile\merged_output_店铺.shp',
# ]

# 3. 读取并合并所有 .shp 文件
gdfs = [gpd.read_file(shp) for shp in shp_paths]
point_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
# print(point_gdf.crs)
# print(point_gdf.shape)

# 2 读取道路数据
for filename in os.listdir(r'E:\work\sv_juanjuanmao\20250308\八条路线'):
    if filename.endswith("01.shp"):
        file_path = os.path.join(r'E:\work\sv_juanjuanmao\20250308\八条路线', filename)
        line_gdf = gpd.read_file(file_path)
        
        # print(line_gdf.columns)
        # print(line_gdf.head())
        # print(line_gdf.shape)
        # print(line_gdf.crs)
        # raise('stop')
        print(file_path)
        # 初始化新的列
        line_gdf['OpenSocial'] = 0

        point_gdf = point_gdf.to_crs(line_gdf.crs)

        point_gdf = point_gdf.to_crs(epsg=32633)
        line_gdf = line_gdf.to_crs(epsg=32633)

        for index, line in line_gdf.iterrows():
            line_geom = line.geometry
            line_length = line_geom.length

            # print(line_length)
            # 距离线段小于20米的所有点
            nearby_points = point_gdf[point_gdf.geometry.distance(line_geom) < 100]
            point_count = len(nearby_points)
            if point_count >0:
                print(line_length,point_count)
                line_gdf.at[index, 'OpenSocial'] = point_count

        # 保存结果到新的文件（可选）
        output_path = file_path.replace('01.shp', '02.shp')
        print(output_path)
        line_gdf = line_gdf.to_crs(epsg=4326)

        line_gdf.to_file(output_path, driver='ESRI Shapefile')


