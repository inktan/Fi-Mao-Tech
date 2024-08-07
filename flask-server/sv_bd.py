# -*- coding: utf-8 -*-
import json
import requests
import time
import os
from PIL import Image
import shutil
from coordinate_converter import transCoordinateSystem, transBmap
import csv
from tqdm import tqdm

class Panorama:
    def __init__(self, pano, year_month, year, month):
        self.pano = pano
        self.year_month = year_month
        self.year = year
        self.month = month

#获取街景对应ID
def get_panoid(lng,lat):
    url = 'https://mapsv0.bdimg.com/?qt=qsdata&x=' + str(lng) + '&y=' + str(lat)
    req = requests.get(url)
    data = json.loads(req.text)
    if (data is not None):
         result = data['content']
         # 输出道路名
         RoadName = result['RoadName']
         # 提取所有历史街景ID
         panoid = result['id']
         url = 'https://mapsv0.bdimg.com/?qt=sdata&sid=' + panoid + '&pc=1'
         r = requests.get(url,stream=True)
         data = json.loads(r.text)
         timeLineIds = data["content"][0]['TimeLine']

         return RoadName,timeLineIds
    else:
        return []

#经纬度坐标转换
# 坐标点类别 1-5-6
coordinate_point_category = 5
def coord_convert(lng1,lat1):
    if coordinate_point_category == 1:
        result = transCoordinateSystem.wgs84_to_gcj02(lng1, lat1)
        result = transCoordinateSystem.gcj02_to_bd09(result[0],result[1])
        return transBmap.lnglattopoint(result[0],result[1])
    elif coordinate_point_category == 5:
        return transBmap.lnglattopoint(lng1,lat1)
    elif coordinate_point_category == 6:
        result = transCoordinateSystem.gcj02_to_bd09(lng1,lat1)
        return transBmap.lnglattopoint(result[0],result[1])
 
def get_lng_lat_info(lng,lat):
        # 1、lat是“latitude”的缩写，纬度
        # 2、lng是“longitude”的缩写，经度
        # 中国的经纬度 经度范围:73°33′E至135°05′E。 纬度范围:3°51′N至53°33′N。

        tar_lng_lat = coord_convert(float(lng),float(lat))
        RoadName,timeLineIds = get_panoid(tar_lng_lat[0],tar_lng_lat[1])
        panoramas = []
        for timeLineId in timeLineIds:
            # panoramas.append(Panorama(timeLineId, timeLineId['TimeLine'], int(timeLineId['TimeLine'][:4]), int(timeLineId['TimeLine'][4:])))
            panoramas.append({
                'pano':timeLineId,
                'id':timeLineId['ID'],
                'road_name':RoadName,
                'year_month':timeLineId['TimeLine'],
                'year':int(timeLineId['TimeLine'][:4]),
                'month':int(timeLineId['TimeLine'][4:])
            })
        return panoramas
        # 筛选2015-2017年中5-9月份的街景
        # 使用列表推导式筛选month大于4小于10的实例
        # filtered_panoramas = [p for p in panoramas if 4 < p.month < 10]
        # filtered_panoramas = [p for p in filtered_panoramas if 2014 < p.year < 2018]
        # if len(filtered_panoramas) == 0:
        #     filtered_panoramas = [p for p in panoramas if 4 < p.month < 10]
                
if __name__ == '__main__':
    get_lng_lat_info(112.2148645,31.04392086)
