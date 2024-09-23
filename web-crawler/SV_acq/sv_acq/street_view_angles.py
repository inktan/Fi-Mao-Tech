
# -*- coding: utf-8 -*-
import json
import requests
import time
import os
from coordinate_converter import transCoordinateSystem, transBmap
import csv
from tqdm import tqdm

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

def get_panoid(lng1,lat1,id,folder_out_path):
    # result = request_url(bound)
    # 使用坐标转换，替代ak密钥
    result = coord_convert(lng1,lat1)
    url = 'https://mapsv0.bdimg.com/?qt=qsdata&x=' + str(result[0]) + '&y=' + str(result[1])
    req = requests.get(url)
    data = json.loads(req.text)
    if (data is not None):
         result = data['content']
         x = result['id']
         RoadName = result['RoadName']
         streetname = str(id) + ',' + str(float(lng1)) + ',' + str(float(lat1)) + ',' + str(RoadName) + '\n'
         with open(folder_out_path+r'/road_name_results.csv', 'a', encoding='utf-8') as f:
             f.write(streetname)
    else:
        result = 0
    return x

def main(csv_path,folder_out_path):
    if os.path.exists(folder_out_path) == False:
        os.mkdir(folder_out_path)
    
    id_lst = []
    lng_lst = []
    lat_lst = []
    # angle_lst = []

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
            # angle_lst.append(row[3])

    with open(folder_out_path+r'/road_name_results.csv','w' ,newline='') as f:
        writer = csv.writer(f)
    with open(folder_out_path+r'/error_data.csv','w' ,newline='') as f:
        writer = csv.writer(f)

    for i in tqdm(range(len(id_lst))):
        # if i<100000:
        #     continue
        # 1、lat是“latitude”的缩写，纬度
        # 2、lng是“longitude”的缩写，经度
        # 中国的经纬度 经度范围:73°33′E至135°05′E。 纬度范围:3°51′N至53°33′N。
        id = id_lst[i]
        lng1 = lng_lst[i]
        lat1 =lat_lst[i]
        # headings = [angle_lst[i]]
        headings = [0,60,120,180,240,300]
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        try:
            # 使用 stream=True 以便在下载大文件时节省内存
            panoid = get_panoid(float(lng1),float(lat1),id,folder_out_path)
            for heading in headings:
                url = 'https://mapsv0.bdimg.com/?qt=pr3d&fovy=100&quality=100&panoid='+str(panoid)+'&heading='+str(heading)+'&pitch=0&width=1000&height=1000'
      
                with requests.get(url, headers=headers, stream=True) as r:
                    # 检查请求是否成功
                    r.raise_for_status()
                    
                    # 确保响应的内容类型是图片
                    if 'image' in r.headers.get('Content-Type', ''):
                        file_path = f'{folder_out_path}/{id}_{lng1}_{lat1}_{heading}.jpg'
                        with open(file_path, 'wb') as fd:
                            for chunk in r.iter_content(chunk_size=8192):
                                fd.write(chunk)
                        print(f"图片已保存到 {file_path}")
                    else:
                        print("请求的内容不是图片")
                        
                    # 稍作延迟，避免请求过于频繁
                    time.sleep(0.03)
                    
        # try:
        #     panoid = get_panoid(float(lng1),float(lat1),id,folder_out_path)
        #     for heading in headings:
        #         url = 'https://mapsv0.bdimg.com/?qt=pr3d&fovy=100&quality=100&panoid='+str(panoid)+'&heading='+str(heading)+'&pitch=0&width=1000&height=1000'
        #         r = requests.get(url,stream=True)
        #         with open(folder_out_path+ '/' + str(id)+"_"+str(lng1)+"_"+str(lat1)+"_" + f'[{heading}].jpg', 'wb') as fd:
        #             fd.write(r.content)
                    # time.sleep(0.03)
                    # for chunk in r.iter_content():
                    #     fd.write(chunk)
        except:
            mistake = str(id) + ',' + str(float(lng1)) + ',' + str(float(lat1)) + ',' + '\n'
            with open(folder_out_path+r'/error_data.csv', 'a', encoding='utf-8') as f:
                f.write(mistake)

if __name__ == '__main__':
    # 文件夹路径
    folder_out_path = r'e:\work\sv_cynthia\sv_points01' # 
    csv_path = r'e:\work\sv_cynthia\points.csv' # 

    main(csv_path,folder_out_path)

