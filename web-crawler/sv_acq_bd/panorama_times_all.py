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

import requests
from PIL import Image
from io import BytesIO
import os

def download_and_merge_streetview(timeLineId, x_count, y_count, save_file_path):
    final_img = Image.new('RGB', (512 * y_count, 512 * x_count), (0, 0, 0))
    
    for x in range(x_count):
        for y in range(y_count):
            # 构造请求URL
            url = (
                'https://mapsv1.bdimg.com/?qt=pdata&sid=' + str(timeLineId) +
                '&pos=' + str(x) + '_' + str(y) +
                '&z=' + str(resolution_ratio) +
                '&udt=20200825&from=PC&auth=GPJbXPMId1MK3NC4B41Mzx7H0%3DNMQDQ%3DuxLEELLENBEtw805wi09v7uvYgP1PcGCgYvjPuVtvYgPMGvgWv%40uVtvYgPPxRYuVtvYgP%40vYZcvWPCuVtvYgP%40ZPcPPuVtvYgPhPPyheuVtvhgMuxVVty1uVtCGYuBtGIiyRWF%3D9Q9K%3DxXw1cv3uVtGccZcuVtPWv3Guxtdw8E62qvyIu9iTHf2PYIUvhgMZSguxzBEHLNRTVtcEWe1GD8zv7u%40ZPuVtc3CuVteuxtf0wd0vyMFFMMFOyAupt66FcErZZWux&seckey=mx8n3s4BT%2BM5jF6vP0bY6%2Bm25GJG9bJAPCy40WbYcVI%3D%2CLObtdXnaK4xy2ePuTyzwbSgjY0lwTkDw27LrZ2b6EqVnuWsCWY8KRbk0pLU3O7nH3Bxrl6QDIDwn3mcxqW8ivuJSq9AWKTb3QWqDwXO1CjnfVgGjLX42xPm511xNwk-n-XPUVVZWEHCymx0r0rAvOnY4vCwIwhNdEUnVTGHwmiRVJeaHB6B6bIKynrJcZMVy'
            )
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                final_img.paste(img, (y * 512, x * 512))  # 粘贴到最终图片
            else:
                print(f"Failed to download image at ({x}, {y}), status code: {response.status_code}")
    
    os.makedirs(os.path.dirname(save_file_path), exist_ok=True)
    final_img.save(save_file_path)
    
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
 
def main(csv_path,folder_out_path):
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
    # df = pd.read_csv(csv_path, encoding='latin1')
    df = pd.read_csv(csv_path)
    # df['name_2'] = df['name_2'].str.encode('latin1').str.decode('utf-8')  # 尝试 latin1 → gbk

    print(df.shape)
    for index, row in tqdm(df.iterrows(),total=df.shape[0]):
        # if index%20!=0:
        #     continue
        # if index <= 1400:
        #     continue
        # if index > 3000:
        #     continue
        print(df.shape[0],index)

        # 1、lat是“latitude”的缩写，纬度
        # 2、lng是“longitude”的缩写，经度
        # 中国的经纬度 经度范围:73°33′E至135°05′E。 纬度范围:3°51′N至53°33′N。
        # print(row)
        # id = int(row['id'])
        # osm_id = row['osm_id']
        lng = row['longitude']
        lat = row['latitude']
        # lng = row['lon']
        # lat = row['lat']
        # mame_2 = row['name_2']
        
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
            # filtered_panoramas = [p for p in filtered_panoramas if 2015 < p.year < 2019]
            filtered_panoramas = panoramas
            # filtered_panoramas = [p for p in filtered_panoramas if p.year == 2021]
            # if len(filtered_panoramas) == 0:
            #     filtered_panoramas = panoramas

            # 是否过滤
            # filtered_panoramas = panoramas
            for i in range(len(filtered_panoramas)):
                pano_id = filtered_panoramas[i].pano['ID']
                year = filtered_panoramas[i].year
                month = filtered_panoramas[i].month

                save_file_path = folder_out_path +'/' + str(int(index)) + '_'+ str(lng) + '_'+ str(lat) +'_'+ str(heading) +'_'+ str(year) +'_'+ str(month) + '.jpg'
                # print(save_file_path,'下载完成')
                # print('count:',count)
                # break

                # if os.path.exists(save_file_path):
                #     print(save_file_path,'已存在')
                    # continue
                    # break
                                
                download_and_merge_streetview(pano_id,x_count,y_count,save_file_path)

                print(save_file_path,'下载完成')
                # continue
                break

        except Exception as e:
            print(f'error:{e}')
            continue
            # mistake = id + ',' + lng+','+lat + ',' + '\n'
            # with open(folder_out_path + '/error_data.csv', 'a', encoding='utf-8') as f:
            #     f.write(mistake)

    
# 1 wgs84
coordinate_point_category = 1

# 5 bd09
# coordinate_point_category = 5

# 6 gcj02
# coordinate_point_category = 6

# 分辨率 "3 - 2048*1096   4 - 4096*2048   4 - 8192*4096"
# resolution_ratio = 3
resolution_ratio = 4
# resolution_ratio = 5

if __name__ == '__main__':
    # 文件夹路径
    csv_path = r'e:\work\20250709_sv_michinen\20251021\points_suply01.csv'  # 需要爬取的点
    folder_out_path = r'e:\work\20250709_sv_michinen\20251021\svi\svi_pan03'  # 保存街景文件

    main(csv_path,folder_out_path)
