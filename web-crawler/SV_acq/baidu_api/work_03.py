# encoding:utf-8
import requests 
from coordinate_converter import transCoordinateSystem, transBmap
from math import radians, cos, sin, asin, sqrt
import csv
import pandas as pd
import random

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

def get_info(address):
    # 设置代理
    ua_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36Chrome 17.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0Firefox 4.0.1',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        ]
    headers = {
            'Connection': 'close',
            "User-Agent": random.choice(ua_list)
        }
    # 一级查询
    url_01 = r'https://shanghai.anjuke.com/community/?kw=%E5%8D%8E%E5%A4%8F%E4%B8%9C%E8%B7%AF2139'
    url = r'https://shanghai.anjuke.com/community/'

    # 二级查询
    # url_02 = r'https://shanghai.anjuke.com/community/view/1406'
    
    params = {"kw":'新粮路755'}
    # response = requests.get(url=url, headers=headers, params=params)
    response = requests.get(url=url_01, params=params)
    
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
## 公园广场个 = 统计该点周边的公园与广场总个数，统计半径为多大
# 运动场馆 = 统计该点周边的运动/场馆总个数，统计半径为多大
## 确定最近公园及其距离  
## 确定最近医院及其距离
## 商场数量 = 统计该点周边的运动/场馆总个数，统计半径为多大
## 确定最近公交车站及其距离
## 车站数量 = 统计该点周边的车站（这个车站指的是公交车站？）总个数，统计半径为多大

csv_path = r'D:\BaiduNetdiskDownload\FiMaoTech\SV_acq\baidu_api\id_address_lng_lat_01.csv'
csv_path = r'e:\work\sv_yueliang\备份小区名_lng_lat_01.csv'
df = pd.read_csv(csv_path)

csv_path = r'D:\BaiduNetdiskDownload\FiMaoTech\SV_acq\baidu_api\id_address_residential_info.csv'
csv_path = r'e:\work\sv_yueliang\备份小区名_lng_lat_anjuke_01.csv'

with open(csv_path ,'w',encoding='utf-8' ,newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id','address','小区名字','均价','竣工时间','总户数','建筑面积','建筑面积/总户数','容积率','绿化率','停车位比','物业费（元）'])

for i,row in enumerate(df.iterrows()):
    print(f'1-{i}')

    info_0 = get_info(row[1]['address'])

    raw_tmp = []
    raw_tmp.append(row[1]['id'])
    raw_tmp.append(row[1]['address'])
    raw_tmp.extend(info_0)

    with open(csv_path ,'a',encoding='utf-8' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(raw_tmp)



