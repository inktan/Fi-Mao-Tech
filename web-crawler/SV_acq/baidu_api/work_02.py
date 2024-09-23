# encoding:utf-8
import requests 
from coordinate_converter import transCoordinateSystem, transBmap
from math import radians, cos, sin, asin, sqrt
import csv
import pandas as pd

def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
 
    # haversine公式
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # 地球平均半径，单位为公里
    return c * r * 1000

def get_total(lng1, lat1, qury_type):
    url = "https://api.map.baidu.com/place/v2/search"
    # 百度api 每天有搜索数量限制
    params = {
        "query":    qury_type,
        "location":    f"{lat1},{lng1}",
        "radius":    "1500",
        "output":    "json",
        "ak":       'qtjtdLI2C7RaEr7PPnbg1FSJljOg4LlI',
        'page_size': 1,
    }

    response = requests.get(url=url, params=params)
    if response:
        response_json = response.json()
        if response_json['status'] == 0:
            results = response_json['results']
            if len(results)==1:
                location= results[0]['location']
                lat2 = location['lat'] #纬度
                lng2 = location['lng'] #经度

                result_01 = transCoordinateSystem.bd09_to_wgs84(float(lng1), float(lat1))
                result_02 = transCoordinateSystem.bd09_to_wgs84(float(lng2), float(lat2))

                dis = haversine(result_01[0], result_01[1], result_02[0], result_02[1]) # 经度1，纬度1，经度2，纬度2 （十进制度数）
                return [response_json['total'], dis]
            
    return [0.0, 0.0]

qury_types = ['公园广场','运动场馆','医院','商场','公交车站','住宅']
# 公园广场个 = 统计该点周边的公园与广场总个数，统计半径为多大
# 运动场馆 = 统计该点周边的运动/场馆总个数，统计半径为多大
# 确定最近公园及其距离  
# 确定最近医院及其距离
# 商场数量 = 统计该点周边的运动/场馆总个数，统计半径为多大
# 确定最近公交车站及其距离
# 车站数量 = 统计该点周边的车站（这个车站指的是公交车站？）总个数，统计半径为多大

csv_path = r'E:\Users\wang.yantao\AppData\Local\Programs\work\work01\id_address_lng_lat_01.csv'
df = pd.read_csv(csv_path)

csv_path = r'E:\Users\wang.yantao\AppData\Local\Programs\work\work01\id_address_lng_lat_total_min_dis_01.csv'

# with open(csv_path ,'w',encoding='utf-8' ,newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(['id','address','lng','lat','公园广场_total','min_dis','运动场馆_total','min_dis','医院_total','min_dis','商场_total','min_dis','公交车站_total','min_dis'])

for i,row in enumerate(df.iterrows()):
    print(f'1-{i}')

    dis_0 = get_total(row[1]['lng'], row[1]['lat'], qury_types[0])
    dis_1 = get_total(row[1]['lng'], row[1]['lat'], qury_types[1])
    dis_2 = get_total(row[1]['lng'], row[1]['lat'], qury_types[2])
    dis_3 = get_total(row[1]['lng'], row[1]['lat'], qury_types[3])
    dis_4 = get_total(row[1]['lng'], row[1]['lat'], qury_types[4])
    dis_5 = get_total(row[1]['lng'], row[1]['lat'], qury_types[5])

    raw_tmp = []
    raw_tmp.append(row[1]['id'])
    raw_tmp.append(row[1]['address'])
    raw_tmp.append(row[1]['lng'])
    raw_tmp.append(row[1]['lat'])
    raw_tmp.extend(dis_0)
    raw_tmp.extend(dis_1)
    raw_tmp.extend(dis_2)
    raw_tmp.extend(dis_3)
    raw_tmp.extend(dis_4)
    raw_tmp.extend(dis_5)

    with open(csv_path ,'a',encoding='utf-8' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(raw_tmp)



