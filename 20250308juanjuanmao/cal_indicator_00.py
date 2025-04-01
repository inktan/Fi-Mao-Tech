import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
import csv

# 1 将语义分析结果转为shp
# 读取语义分析数据
ss_path = r'e:\work\sv_juanjuanmao\ss.csv'  # 替换为你的第一个CSV文件的路径  
ss_df = pd.read_csv(ss_path)
# 使用rename()方法重命名列
ss_df = ss_df.rename(columns={'id': 'iamge_name'})

# 使用 _ 对 iamge_name 列进行分列
split_columns = ss_df['iamge_name'].str.split('_', expand=True)

# 提取前四列并命名为 id, lon, lat, degree
split_columns = split_columns.iloc[:, :4]
split_columns.columns = ['id', 'lon', 'lat', 'degree']

# 将提取的列合并到原数据中
ss_df = pd.concat([ss_df, split_columns], axis=1)

# 删除 degree 列中的 .jpg 后缀
ss_df['degree'] = ss_df['degree'].str.replace('.jpg', '', regex=False)

dst_crs = 'EPSG:4326'
ss_gdf = gpd.GeoDataFrame(ss_df, geometry=gpd.points_from_xy(ss_df.lon, ss_df.lat), crs=dst_crs)

# for i in ss_gdf.columns:
#     print(i)
# print(ss_gdf.columns)
# print(ss_gdf.head())
# print(ss_gdf.shape)
# print(ss_gdf.crs)
# raise('stop')

# 2 读取道路数据
for filename in os.listdir(r'E:\work\sv_juanjuanmao\20250308\八条路线'):
    if filename.endswith("_SEG.shp"):
        file_path = os.path.join(r'E:\work\sv_juanjuanmao\20250308\八条路线', filename)
        line_gdf = gpd.read_file(file_path)
        
        # print(line_gdf.columns)
        # print(line_gdf.head())
        # print(line_gdf.shape)
        # print(line_gdf.crs)
        # raise('stop')
        # 初始化新的列
        line_gdf['ashcan_sum'] = 0
        line_gdf['poster_sum'] = 0
        line_gdf['green_sum'] = 0
        line_gdf['window_sum'] = 0
        line_gdf['chair_sum'] = 0

        ss_gdf = ss_gdf.to_crs(epsg=32633)
        line_gdf = line_gdf.to_crs(epsg=32633)

        for index, line in line_gdf.iterrows():
            line_geom = line.geometry
            line_length = line_geom.length

            # print(line_length)
            # 距离线段小于20米的所有点
            nearby_points = ss_gdf[ss_gdf.geometry.distance(line_geom) < 25]
            point_count = len(nearby_points)
            if point_count >0:

                # 计算 垃圾箱密度 
                ashcan_sum = nearby_points['ashcan;trash;can;garbage;can;wastebin;ash;bin;ash-bin;ashbin;dustbin;trash;barrel;trash;bin'].sum()
                # 计算 广告牌密度 
                poster_sum = nearby_points['poster;posting;placard;notice;bill;card'].sum()
                # 计算 绿视率 
                green_sum = nearby_points['tree'].sum()
                green_sum += nearby_points['grass'].sum()
                green_sum += nearby_points['plant;flora;plant;life'].sum()
                # 计算 透明率 
                window_sum = nearby_points['windowpane;window'].sum()
                # 计算 座椅密度
                chair_sum = nearby_points['chair'].sum()
                chair_sum += nearby_points['armchair'].sum()
                chair_sum += nearby_points['swivel;chair'].sum()

                # 将计算结果添加到当前行
                line_gdf.at[index, 'ashcan_sum'] = ashcan_sum
                line_gdf.at[index, 'poster_sum'] = poster_sum
                line_gdf.at[index, 'green_sum'] = green_sum
                line_gdf.at[index, 'window_sum'] = window_sum
                line_gdf.at[index, 'chair_sum'] = chair_sum

                print(line_length,ashcan_sum,poster_sum,green_sum,window_sum,chair_sum)
                # break
                        
        # 保存结果到新的文件（可选）
        output_path = file_path.replace('_SEG.shp', '_SEG_ssindicators.shp')
        line_gdf = line_gdf.to_crs(epsg=4326)

        line_gdf.to_file(output_path, driver='ESRI Shapefile')