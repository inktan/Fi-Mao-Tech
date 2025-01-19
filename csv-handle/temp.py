
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

#获取街景对应ID
def get_panoid(lng,lat):
    url = 'https://mapsv0.bdimg.com/?qt=qsdata&x=' + str(lng) + '&y=' + str(lat)

    for i in range(3):
        try:
            req = requests.get(url)
            data = json.loads(req.text)
            if (data is not None):
                if 'content' in data:
                    result = data['content']
                    # 提取所有历史街景ID
                    panoid = result['id']
                    url = 'https://mapsv0.bdimg.com/?qt=sdata&sid=' + panoid + '&pc=1'
                    
                    for j in range(3):
                        try:
                            r = requests.get(url,stream=True)
                            data = json.loads(r.text)
                            if (data is not None):
                                if 'content' in data:
                                    results = data['content']
                                    if len(results) > 0:
                                        # 提取所有历史街景ID
                                        if 'TimeLine' in results[0]:
                                            timeLineIds = results[0]['TimeLine']
                                            return timeLineIds 
                                             
                        except Exception as e:
                            print(e)
                            print('retrying...')
                            time.sleep(2)     
                                                                    
        except Exception as e:
            print(e)
            print('retrying...')
            time.sleep(2)

    return []

#经纬度坐标转换
# 坐标点类别 1-5-6
coordinate_point_category = 1
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
 
resolution_ratio = 4
def main(csv_path,sv_infos_path):
    # 创建一个空列表来存储行数据  
    rows = []  
    df = pd.read_csv(csv_path)
    print(df.shape)

    # 遍历每一行数据  
    count=0
    for index, row in tqdm(df.iterrows()):  
        # if index<1104645:
        #     continue
        # 1、lat是“latitude”的缩写，纬度
        # 2、lng是“longitude”的缩写，经度
        # 中国的经纬度 经度范围:73°33′E至135°05′E。 纬度范围:3°51′N至53°33′N。
        # print(row)
        # print(row['id'])
        # print(row['longitude'])
        # print(row['latitude'])
        # print(row['name'])
        # print(row['type'])
        # print(row['oneway'])
        # print(row['bridge'])
        # print(row['tunnel'])
        # break

        tar_lng_lat = coord_convert(float(row['longitude']),float(row['latitude']))
        print(index,tar_lng_lat)
        print(df.shape)

        # break
        timeLineIds = get_panoid(tar_lng_lat[0],tar_lng_lat[1])
        # if len(timeLineIds)>0:
        #     print(timeLineIds)
        #     break
        for timeLine in timeLineIds:
            with open(sv_infos_path,'a' ,newline='') as f:
                writer = csv.writer(f)
                writer.writerow([count,float(row['longitude']),float(row['latitude']),row['name'],row['type'],row['oneway'],row['bridge'],row['tunnel'],timeLine['ID'], timeLine['TimeLine'], timeLine['Year']])
                count+=1
                break

        # if index>=11850:
        #     break

if __name__ == '__main__':
    # 文件夹路径
    csv_path = r'/home/ubuntu/SV_acq/澳门特别行政区_立方数据学社_15m_01.csv' # 需要爬取的点
    sv_infos_path = csv_path.replace('_.csv','_sv_infos_.csv')

    with open(sv_infos_path,'w' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id','longitude','latitude','name','type','oneway','bridge','tunnel','ID','timeLine','year'])

    main(csv_path,sv_infos_path)


