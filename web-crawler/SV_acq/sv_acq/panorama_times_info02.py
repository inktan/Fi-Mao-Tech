
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

def get_streetview(result_cache_path,timeLineId,x_count,y_count):
    for x in range(x_count):
        for y in range(y_count):
            url = 'https://mapsv1.bdimg.com/?qt=pdata&sid=' + str(timeLineId) + '&pos=' + str(x) + '_' + str(y) + '&z=' + str(resolution_ratio) + '&udt=20200825&from=PC&auth=GPJbXPMId1MK3NC4B41Mzx7H0%3DNMQDQ%3DuxLEELLENBEtw805wi09v7uvYgP1PcGCgYvjPuVtvYgPMGvgWv%40uVtvYgPPxRYuVtvYgP%40vYZcvWPCuVtvYgP%40ZPcPPuVtvYgPhPPyheuVtvhgMuxVVty1uVtCGYuBtGIiyRWF%3D9Q9K%3DxXw1cv3uVtGccZcuVtPWv3Guxtdw8E62qvyIu9iTHf2PYIUvhgMZSguxzBEHLNRTVtcEWe1GD8zv7u%40ZPuVtc3CuVteuxtf0wd0vyMFFMMFOyAupt66FcErZZWux&seckey=mx8n3s4BT%2BM5jF6vP0bY6%2Bm25GJG9bJAPCy40WbYcVI%3D%2CLObtdXnaK4xy2ePuTyzwbSgjY0lwTkDw27LrZ2b6EqVnuWsCWY8KRbk0pLU3O7nH3Bxrl6QDIDwn3mcxqW8ivuJSq9AWKTb3QWqDwXO1CjnfVgGjLX42xPm511xNwk-n-XPUVVZWEHCymx0r0rAvOnY4vCwIwhNdEUnVTGHwmiRVJeaHB6B6bIKynrJcZMVy'
            r = requests.get(url,stream=True)
            with open(result_cache_path + '/' + str(x) + '_' + str(y) + '.jpg', 'wb') as fd:
                time.sleep(0.03)
                for chunk in r.iter_content():
                    fd.write(chunk)

def merge_image(result_cache_path, id,lng,lat,x_count,y_count,save_file_path,timeLine):
    img2 = Image.new('RGB', (512 * y_count,512 * x_count), (0, 0, 0))
    for y in range(int(y_count)):
        for x in range(int(x_count)):
            im_path = result_cache_path + '/' + str(x) + '_' + str(y) + '.jpg'
            img = Image.open(im_path)
            img2.paste(img, (y * 512, x * 512))

    # name = save_file_path + '/' + str(id)+'_' +str(lng)+'_' +str(lat)+ '_' +timeLine+ '.jpg'
    name = save_file_path + '/' + str(id)+ '_' +timeLine+ '.jpg'
    img2.save(name)
    shutil.rmtree(result_cache_path, ignore_errors=True)

#获取街景对应ID
def get_panoid(lng,lat,bound,sv_id,folder_out_path):
    url = 'https://mapsv0.bdimg.com/?qt=qsdata&x=' + str(lng) + '&y=' + str(lat)
    req = requests.get(url)
    data = json.loads(req.text)
    if (data is not None):
         result = data['content']

         # 输出道路名
        #  RoadName = result['RoadName']
        #  streetname = sv_id + ',' + bound + ',' + str(RoadName) + '\n'
        #  with open( folder_out_path+ '/road_name_results.csv', 'a', encoding='utf-8') as f:
        #      f.write(streetname)

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
def main(csv_path,folder_out_path):
    # if os.path.exists(folder_out_path) == False:
    #     os.makedirs(folder_out_path)

    # 分辨率 "3 - 2048*1024   4 - 4096*2048"
    # if(resolution_ratio == 3):
    #     ratio = 8
    # else:
    #     ratio = 32

    # x_count = int(2 ** (resolution_ratio - 2))
    # y_count = int(x_count * 2)

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

    #临时文件夹位置
    # temp_path = folder_out_path + '/data stream file (can be deleted after crawling)'
    # if os.path.exists(temp_path) == False:
    #     os.makedirs(temp_path)

    # 记录信息的csv文件
    # with open(folder_out_path+r'/road_name_results.csv','w' ,newline='') as f:
    #     writer = csv.writer(f)
    # with open(folder_out_path+r'/error_data.csv','w' ,newline='') as f:
    #     writer = csv.writer(f)
    
    for i in tqdm(range(len(id_lst))):
        # if i<835:
        #     continue
        # 1、lat是“latitude”的缩写，纬度
        # 2、lng是“longitude”的缩写，经度
        # 中国的经纬度 经度范围:73°33′E至135°05′E。 纬度范围:3°51′N至53°33′N。
        id = id_lst[i]
        lng = lng_lst[i]
        lat =lat_lst[i]
        try:
            tar_lng_lat = coord_convert(float(lng),float(lat))
            timeLineIds = get_panoid(tar_lng_lat[0],tar_lng_lat[1],lng+'_'+lat, id,folder_out_path)

            # 每个地点单独存一个文件夹，使用id命名
            # pic_path = folder_out_path +'/'+str(id)+'_' +str(lng)+'_' +str(lat)
            # pic_path = folder_out_path +'/'+str(id)
            # if os.path.exists(pic_path) == False:
            #     os.makedirs(pic_path)

            for timeLine in timeLineIds:

                with open(r'e:\work\sv_畫畫_20240923\aomen_sv_info.csv','a' ,newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([id,lng,lat, timeLine['TimeLine'], timeLine['Year']])
                # result_cache_path = temp_path + '/'+str(id)+'_'+ timeLine['ID'] +'_'+ timeLine['TimeLine']
                # if os.path.exists(result_cache_path) == False:
                #     os.makedirs(result_cache_path)
                # get_streetview(result_cache_path ,timeLine['ID'] ,x_count,y_count)
                # merge_image(result_cache_path, id,lng,lat,x_count,y_count,pic_path,timeLine['TimeLine'])

        except:
            print("There is no streetview in the current location")
            # mistake = id + ',' + lng+','+lat + ',' + '\n'
            # with open(folder_out_path + '/error_data.csv', 'a', encoding='utf-8') as f:
            #     f.write(mistake)

if __name__ == '__main__':
    # 文件夹路径
    csv_path = r'e:\work\sv_畫畫_20240923\aomen_01.csv' # 需要爬取的点
    folder_out_path = r'e:\work\20240201\sv' # 保存街景文件

    with open(r'e:\work\sv_畫畫_20240923\aomen_sv_info.csv','w' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id','lng','lat','timeLine','year'])

    main(csv_path,folder_out_path)
