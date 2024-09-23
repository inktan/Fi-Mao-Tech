import csv
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import csv
from tqdm import tqdm
import numpy as np

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

df_point = pd.read_csv(r'e:\work\sv_kaixindian\points.csv')
df_gongjiao = pd.read_csv(r'f:\2022poi\2022POI\华东poi1\上海市\上海市POI数据_故居_博物馆_纪念馆_no_parking.csv')
csv_path_gongjiao = r'E:\work\sv_kaixindian\03-poi\points_故居_博物馆_纪念馆.csv'

point_coords = df_point[['lng', 'lat']].to_numpy()
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
    valid_distances = distances[distances <= 500]
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

