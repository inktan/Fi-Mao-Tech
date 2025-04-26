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

def get_streetview(result_cache_path,timeLineId,x_count,y_count):
    for x in range(x_count):
        for y in range(y_count):
            url = 'https://mapsv1.bdimg.com/?qt=pdata&sid=' + str(timeLineId) + '&pos=' + str(x) + '_' + str(y) + '&z=' + str(resolution_ratio) + '&udt=20200825&from=PC&auth=GPJbXPMId1MK3NC4B41Mzx7H0%3DNMQDQ%3DuxLEELLENBEtw805wi09v7uvYgP1PcGCgYvjPuVtvYgPMGvgWv%40uVtvYgPPxRYuVtvYgP%40vYZcvWPCuVtvYgP%40ZPcPPuVtvYgPhPPyheuVtvhgMuxVVty1uVtCGYuBtGIiyRWF%3D9Q9K%3DxXw1cv3uVtGccZcuVtPWv3Guxtdw8E62qvyIu9iTHf2PYIUvhgMZSguxzBEHLNRTVtcEWe1GD8zv7u%40ZPuVtc3CuVteuxtf0wd0vyMFFMMFOyAupt66FcErZZWux&seckey=mx8n3s4BT%2BM5jF6vP0bY6%2Bm25GJG9bJAPCy40WbYcVI%3D%2CLObtdXnaK4xy2ePuTyzwbSgjY0lwTkDw27LrZ2b6EqVnuWsCWY8KRbk0pLU3O7nH3Bxrl6QDIDwn3mcxqW8ivuJSq9AWKTb3QWqDwXO1CjnfVgGjLX42xPm511xNwk-n-XPUVVZWEHCymx0r0rAvOnY4vCwIwhNdEUnVTGHwmiRVJeaHB6B6bIKynrJcZMVy'
            r = requests.get(url,stream=True)
            with open(result_cache_path + '/' + str(x) + '_' + str(y) + '.jpg', 'wb') as fd:
                time.sleep(0.03)
                for chunk in r.iter_content():
                    fd.write(chunk)

def merge_image(result_cache_path, x_count,y_count,save_file_path):
    img2 = Image.new('RGB', (512 * y_count,512 * x_count), (0, 0, 0))
    for y in range(int(y_count)):
        for x in range(int(x_count)):
            im_path = result_cache_path + '/' + str(x) + '_' + str(y) + '.jpg'
            img = Image.open(im_path)
            img2.paste(img, (y * 512, x * 512))

    img2.save(save_file_path)
    shutil.rmtree(result_cache_path, ignore_errors=True)

#获取街景对应ID
def get_panoid(lng,lat,bound,sv_id,folder_out_path):
    url = 'https://mapsv0.bdimg.com/?qt=qsdata&x=' + str(lng) + '&y=' + str(lat)
    req = requests.get(url)
    data = json.loads(req.text)
    # print('data')
    # print(data)
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
         Heading = data["content"][0]['Heading']
         MoveDir = data["content"][0]['MoveDir']
         NorthDir = data["content"][0]['NorthDir']

         return [timeLineIds,Heading,MoveDir, NorthDir]
    else:
        return []

#经纬度坐标转换
# 坐标点类别 1-5-6

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
 
# def main(csv_path,folder_out_path):
def main(folder_out_path):
    if os.path.exists(folder_out_path) == False:
        os.mkdir(folder_out_path)

    # if(resolution_ratio == 3):
    #     ratio = 8
    # else:
    #     ratio = 32

    # 分辨率 "3 - 2048*1096   4 - 4096*2048"
    x_count = int(2 ** (resolution_ratio - 2))
    y_count = int(x_count * 2)
    # 3 2 2*2 = 8
    # 3 4 4*2 = 32
    # 读取经纬度坐标点

    #临时文件夹位置
    temp_path = folder_out_path + '/data stream file (can be deleted after crawling)'
    if os.path.exists(temp_path) == False:
        os.makedirs(temp_path)
    
    try:
        pic_path = folder_out_path +'/sv_pan05'
        if os.path.exists(pic_path) == False:
            os.makedirs(pic_path)

        save_file_path = pic_path + '/' + 'pano_id_'+ str(pano_id)+ '.jpg'
        if os.path.exists(save_file_path):
            print(save_file_path,'已存在')
            # break
            return
        
        result_cache_path = temp_path + '/'+'pano_id_'+ pano_id
        if os.path.exists(result_cache_path) == False:
            os.makedirs(result_cache_path)
        get_streetview(result_cache_path ,pano_id ,x_count,y_count)
        merge_image(result_cache_path, x_count,y_count,save_file_path)
        print(save_file_path,'下载完成')
        return
        # break

    except Exception as e:
        # continue
        print(f'error:{e}')
        return

coordinate_point_category = 1
# 分辨率 "3 - 2048*1096   4 - 4096*2048"
# resolution_ratio = 4
resolution_ratio = 5

if __name__ == '__main__':
    # 文件夹路径
    # csv_path = r'e:\work\sv_quanzhou\泉州市_100m_unique_Spatial_Balance.csv' # 需要爬取的点
    folder_out_path = r'C:\Users\user.wang\Pictures\sv_pan_work' # 保存街景文件
    pano_id = r'09025200121709051540081197O'

    # main(csv_path,folder_out_path)
    main(folder_out_path)
