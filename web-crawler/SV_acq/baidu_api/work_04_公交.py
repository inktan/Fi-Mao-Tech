import csv
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import csv
from tqdm import tqdm
import numpy as np
import os

def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees), returns an array.
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = np.radians([lon1, lat1, lon2, lat2])
    
    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371 # 地球平均半径，单位为公里
    return c * r * 1000

# df_point = pd.read_csv(r'e:\work\sv_kaixindian\points.csv')
csv_path = r'e:\work\sv_yueliang\备份小区名_lng_lat_01.csv'
df_point = pd.read_csv(csv_path, encoding='gbk')

# poi_name = r'上海市POI数据_餐饮店_咖啡店.csv'
# poi_name = r'上海市POI数据_公交站.csv'
# poi_name = r'上海市POI数据_公园_广场.csv'
# poi_name = r'上海市POI数据_故居_博物馆_纪念馆_no_parking.csv'
# poi_name = r'上海市POI数据_商场.csv'
# poi_name = r'上海市POI数据_手工艺品店_零售店_商店.csv'
# poi_name = r'上海市POI数据_停车场.csv'
# poi_name = r'上海市POI数据_小区_no_parking.csv'
# poi_name = r'上海市POI数据_医院_诊所.csv'
poi_name = r'上海市POI数据_运动.csv'

poi_folder = r'f:\2022poi\2022POI\华东poi1\上海市'
df_gongjiao = pd.read_csv(os.path.join(poi_folder, poi_name))
out_folder = r'e:\work\sv_yueliang'
csv_path_gongjiao = os.path.join(out_folder, poi_name.replace('上海市POI数据_', '备份小区名_lng_lat_'))

point_coords = df_point[['lng_wgs84', 'lat_wgs84']].to_numpy()
gongjiao_coords = df_gongjiao[['经度', '纬度']].to_numpy()

results = []
for i, (lng, lat) in enumerate(tqdm(point_coords)):
    # 将lng和lat转换为numpy数组，形状与gongjiao_coords相同
    # 将lng和lat重复，使其与gongjiao_coords的形状匹配
    try:
        lng_rep = np.repeat(float(lng), len(gongjiao_coords))
        lat_rep = np.repeat(float(lat), len(gongjiao_coords))
    except:
        results.append([df_point['id'][i], 0, 0, 0])
        continue

    distances = haversine_np(lng_rep , lat_rep , gongjiao_coords[:, 0], gongjiao_coords[:, 1])
    valid_distances = distances[distances <= 1500]
    print(valid_distances)
    if valid_distances.size == 0:
        results.append([df_point['id'][i], 0, 0, 0])
        continue
    
    # 找到最小距离的索引值
    min_distance_index = np.argmin(distances)
    results.append([df_point['id'][i], len(valid_distances), df_gongjiao['名称'][min_distance_index], distances[min_distance_index]])

with open(csv_path_gongjiao, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'count_', 'name', 'min_distance'])
    writer.writerows(results)

