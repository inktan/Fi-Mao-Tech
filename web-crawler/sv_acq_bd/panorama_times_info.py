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
import pandas as pd

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
    # print('data')
    # print(data)
    if (data is not None):
         result = data['content']

         # 提取所有历史街景ID
         panoid = result['id']
         url = 'https://mapsv0.bdimg.com/?qt=sdata&sid=' + panoid + '&pc=1'
         r = requests.get(url,stream=True)
         data = json.loads(r.text)
         timeLineIds = data["content"][0]['TimeLine']
         Heading = data["content"][0]['Heading']
         MoveDir = data["content"][0]['MoveDir']
         NorthDir = data["content"][0]['NorthDir']

         return [timeLineIds,Heading,MoveDir, NorthDir]
    else:
        return []
 
def main():
    df = pd.read_csv(csv_path)
    # df['name_2'] = df['name_2'].str.encode('latin1').str.decode('utf-8')  # 尝试 latin1 → gbk

    print(df.shape)
    for index, row in tqdm(df.iterrows()):
        # if index <= 1000:
        #     continue
        # if index >1000000:
        #     continue
        print(df.shape[0],index)

        # 1、lat是“latitude”的缩写，纬度
        # 2、lng是“longitude”的缩写，经度
        # 中国的经纬度 经度范围:73°33′E至135°05′E。 纬度范围:3°51′N至53°33′N。
        # print(row)
        lng = row['longitude']
        lat = row['latitude']
        # lng = row['lon']
        # lat = row['lat']
        
        try:
            tar_lng_lat = coord_convert(lng,lat)
            # print(tar_lng_lat)
            panoidInfos = get_panoid(tar_lng_lat[0],tar_lng_lat[1])
            timeLineIds = panoidInfos[0]
            heading = panoidInfos[1]
            # print(panoidInfos)
            # break

            panoramas = []
            for timeLineId in timeLineIds:
                panoramas.append(Panorama(timeLineId, timeLineId['TimeLine'], int(timeLineId['TimeLine'][:4]), int(timeLineId['TimeLine'][4:])))

            # 筛选2015-2017年中5-9月份的街景
            # 使用列表推导式筛选month大于4小于10的实例
            # filtered_panoramas = [p for p in panoramas  if p.month in [6, 7, 8]]
            filtered_panoramas = panoramas
            # filtered_panoramas = [p for p in filtered_panoramas if 2015 < p.year < 2019]
            # if len(filtered_panoramas) == 0:
            #     filtered_panoramas = panoramas

            # 是否过滤
            # filtered_panoramas = panoramas
            for i in range(len(filtered_panoramas)):
                pano_id = filtered_panoramas[i].pano['ID']
                timeLine = filtered_panoramas[i].pano['TimeLine']
                year = filtered_panoramas[i].year
                month = filtered_panoramas[i].month

                with open(sv_infos_path,'a' ,newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([index,float(row['longitude']),float(row['latitude']), pano_id, year, month])


        except Exception as e:
            print(f'error:{e}')
            continue

coordinate_point_category = 1
# coordinate_point_category = 5
# coordinate_point_category = 6

#经纬度坐标转换
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
    
if __name__ == '__main__':
    # 文件夹路径
    csv_path = r'f:\立方数据\2025年道路数据\【立方数据学社】北京市\北京市_50m_Spatial.csv'  # 需要爬取的点
    sv_infos_path = csv_path.replace('.csv','_infos.csv')

    with open(sv_infos_path,'w' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['index','osm_id','longitude','latitude','year','month'])

    main()
