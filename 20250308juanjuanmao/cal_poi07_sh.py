import os
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString

# Define the POI shp paths with their categories
poi_categories = {
    '餐饮服务': r'F:\立方数据\上海poi\上海市2020\shp\上海市_餐饮服务.shp',
    '购物服务': r'F:\立方数据\上海poi\上海市2020\shp\上海市_购物服务.shp',
    '生活服务': r'F:\立方数据\上海poi\上海市2020\shp\上海市_生活服务.shp',
    '体育休闲服务': r'F:\立方数据\上海poi\上海市2020\shp\上海市_体育休闲服务.shp',
    '医疗保健服务': r'F:\立方数据\上海poi\上海市2020\shp\上海市_医疗保健服务.shp',
    '住宿服务': r'F:\立方数据\上海poi\上海市2020\shp\上海市_住宿服务.shp',
    '金融保险服务': r'F:\立方数据\上海poi\上海市2020\shp\上海市_金融保险服务.shp',
    # '教育培训': r'',
    # '文化传媒机构': r'',
    '交通设施': r'F:\立方数据\上海poi\上海市2020\shp\上海市_交通设施服务.shp',
    '政府机构及社会团体': r'F:\立方数据\上海poi\上海市2020\shp\上海市_政府机构及社会团体.shp', 
    '公司企业': r'F:\立方数据\上海poi\上海市2020\shp\上海市_公司企业.shp',
    '汽车服务': r'F:\立方数据\上海poi\上海市2020\shp\上海市_汽车服务.shp',
    # '房地产': r'',
    # '自然地理': r'',
    '公共设施': r'F:\立方数据\上海poi\上海市2020\shp\上海市_公共设施.shp',

    '道路附属设施':r'F:\立方数据\上海poi\上海市2020\shp\上海市_道路附属设施.shp',
    '地名地址信息':r'F:\立方数据\上海poi\上海市2020\shp\上海市_地名地址信息.shp',
    '风景名胜':r'F:\立方数据\上海poi\上海市2020\shp\上海市_风景名胜.shp',
    '科教文化服务':r'F:\立方数据\上海poi\上海市2020\shp\上海市_科教文化服务.shp',
    '摩托车服务':r'F:\立方数据\上海poi\上海市2020\shp\上海市_摩托车服务.shp',
    '汽车维修':r'F:\立方数据\上海poi\上海市2020\shp\上海市_汽车维修.shp',
    '汽车销售':r'F:\立方数据\上海poi\上海市2020\shp\上海市_汽车销售.shp',
    '商务住宅':r'F:\立方数据\上海poi\上海市2020\shp\上海市_商务住宅.shp',
    '室内设施':r'F:\立方数据\上海poi\上海市2020\shp\上海市_室内设施.shp',
    '通行设施':r'F:\立方数据\上海poi\上海市2020\shp\上海市_通行设施.shp',
}

# excel_path = r'e:\work\sv_kaixindian\长春.xlsx'
# df = pd.read_excel(excel_path, engine='openpyxl')
excel_path = r'e:\work\sv_kaixindian\20250724\points.csv'
df = pd.read_csv(excel_path, )

geometry = [Point(xy) for xy in zip(df['lng'], df['lat'])]
gdf_points = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326").to_crs(epsg=32633)  # WGS84坐标系统

# 为每个POI类别添加计数列，初始化为0
for category in poi_categories.keys():
    gdf_points[f'{category}_count'] = 0

for index, row in gdf_points.iterrows():
    point = row.geometry
    buffer = point.buffer(500)  # 1500米缓冲区
    for category, path in poi_categories.items():
        try:
            # 读取POI数据并转换坐标系
            # poi_gdf = gpd.read_file(path).to_crs(epsg=32633)
            poi_gdf = gpd.read_file(path,encoding='gb18030').to_crs(epsg=32633)
            # 计算缓冲区内的POI数量
            count = poi_gdf[poi_gdf.geometry.within(buffer)].shape[0]
            gdf_points.at[index, f'{category}_count'] = count
        except Exception as e:
            print(f"处理{category}时出错: {e}")
            gdf_points.at[index, f'{category}_count'] = -1  # 用-1表示错误

    # 打印进度
    if (index + 1) % 10 == 0:
        print(f"已处理 {index + 1}/{len(gdf_points)} 个点")


output_csv = r'e:\work\sv_kaixindian\20250724\上海市2020_500_poi统计.csv'
gdf_points.drop(columns=['geometry']).to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"处理完成，结果已保存到: {output_csv}")
