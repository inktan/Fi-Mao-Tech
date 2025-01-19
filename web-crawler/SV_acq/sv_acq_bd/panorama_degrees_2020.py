
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

import requests
from PIL import Image
from io import BytesIO

class Panorama:
    def __init__(self, pano, year_month, year, month):
        self.pano = pano
        self.year_month = year_month
        self.year = year
        self.month = month

def get_streetview(result_cache_path,timeLineId,degree):
    url = f'https://mapsv0.bdimg.com/?qt=pr3d&fovy=90&quality=100&panoid={timeLineId}&heading={degree}&pitch=0&width=960&height=960'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    while True:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image.save(result_cache_path + '_' + str(degree) + '.png', "PNG")
                break
        except requests.ConnectionError:
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)

#获取街景对应ID
def get_panoid(lng,lat,bound,sv_id,folder_out_path):
    url = 'https://mapsv0.bdimg.com/?qt=qsdata&x=' + str(lng) + '&y=' + str(lat)
    req = requests.get(url)
    data = json.loads(req.text)
    if (data is not None):
         result = data['content']

         # 输出道路名
         RoadName = result['RoadName']
         streetname = sv_id + ',' + bound + ',' + str(RoadName) + '\n'
         with open( folder_out_path+ '/road_name_results.csv', 'a', encoding='utf-8') as f:
             f.write(streetname)

         # 提取所有历史街景ID
         panoid = result['id']
         url = 'https://mapsv0.bdimg.com/?qt=sdata&sid=' + panoid + '&pc=1'
         r = requests.get(url,stream=True)
         data = json.loads(r.text)
         timeLineIds = data["content"][0]['TimeLine']

         return timeLineIds
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
 
def main(csv_path,folder_out_path):

    # 读取经纬度坐标点
    id_lst = []
    lng_lst = []
    lat_lst = []
    with open(csv_path, 'r') as csv_file:  
        # 创建CSV阅读器对象  
        csv_reader = csv.reader(csv_file)
        # 跳过标题行  
        next(csv_reader)
        # 遍历剩余的行  
        for row in csv_reader:  
            # 打印行内容  
            id_lst.append(row[0])
            lng_lst.append(row[1])
            lat_lst.append(row[2])
        
    # 记录信息的csv文件
    with open(folder_out_path+r'/road_name_results.csv','w' ,newline='') as f:
        writer = csv.writer(f)
    with open(folder_out_path+r'/error_data.csv','w' ,newline='') as f:
        writer = csv.writer(f)
    
    for j in tqdm(range(len(id_lst))):
        # if j<=100:
        #     continue
        # if j>5000:
        #     continue

        # 1、lat是“latitude”的缩写，纬度
        # 2、lng是“longitude”的缩写，经度
        # 中国的经纬度 经度范围:73°33′E至135°05′E。 纬度范围:3°51′N至53°33′N。
        id = id_lst[j]
        lng = lng_lst[j]
        lat =lat_lst[j]
        try:
            tar_lng_lat = coord_convert(float(lng),float(lat))

            timeLineIds = get_panoid(tar_lng_lat[0],tar_lng_lat[1],lng+'_'+lat, id,folder_out_path)

            panoramas = []
            for timeLineId in timeLineIds:
                panoramas.append(Panorama(timeLineId, timeLineId['TimeLine'], int(timeLineId['TimeLine'][:4]), int(timeLineId['TimeLine'][4:])))

            # 筛选2015-2017年中5-9月份的街景
            # 使用列表推导式筛选month大于4小于10的实例
            filtered_panoramas = [p for p in panoramas if 4 < p.month < 10]
            # filtered_panoramas = [p for p in filtered_panoramas if 2014 < p.year < 2018]
            if len(filtered_panoramas) == 0:
                filtered_panoramas = [p for p in panoramas if 4 < p.month < 10]
            if len(filtered_panoramas) == 0:
                filtered_panoramas = panoramas

            for i in range(len(filtered_panoramas)):
                pano_id = filtered_panoramas[i].pano['ID']
                timeLine = filtered_panoramas[i].pano['TimeLine']
                year = filtered_panoramas[i].year
                month = filtered_panoramas[i].month

                #储存街景的文件夹位置
                result_cache_path = folder_out_path + '/'+str(id)+ timeLine
                for degree in [0,90,180,270]:
                    get_streetview(result_cache_path ,pano_id ,degree)
                
                break

        except Exception as e:
            print(e)
            print("There is no streetview in the current location")
            mistake = id + ',' + lng+','+lat + ',' + '\n'
            with open(folder_out_path + '/error_data.csv', 'a', encoding='utf-8') as f:
                f.write(mistake)


resolution_ratio = 4
if __name__ == '__main__':
    # 文件夹路径
    csv_path = r'e:\work\sv_20240918\20240918Export_Output.csv' # 需要爬取的点
    folder_out_path = r'e:\work\sv_20240918\sv_degrees' # 保存街景文件
    if os.path.exists(folder_out_path) == False:
        os.makedirs(folder_out_path)
    main(csv_path,folder_out_path)
