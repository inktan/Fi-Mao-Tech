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
import requests
import time
from pathlib import Path

def download_baidu_panorama(
    save_path,          # 保存路径，例如 "C:/images/panorama.jpg"
    panoid,            # 全景ID，例如 "09000300122002141605289265F"
    fovy=90,           # 垂直视角，默认90
    heading=0,         # 水平方向角度，默认0
    pitch=0,           # 垂直方向角度，默认0
    width=1000,        # 图片宽度，默认1000
    height=500,        # 图片高度，默认500
    max_retries=3,     # 最大重试次数，默认3
    retry_delay=1      # 重试延迟(秒)，默认1
):
    """
    下载百度街景图片并保存到本地
    
    参数:
        save_path: 图片保存路径
        panoid: 全景ID
        fovy: 垂直视角(默认90)
        heading: 水平方向角度(默认0)
        pitch: 垂直方向角度(默认0)
        width: 图片宽度(默认1000)
        height: 图片高度(默认500)
        max_retries: 最大重试次数(默认3)
        retry_delay: 重试延迟(秒，默认1)
        
    返回:
        bool: 下载成功返回True，失败返回False
    """
    base_url = "https://mapsv0.bdimg.com/"
    params = {
        'qt': 'pr3d',
        'fovy': fovy,
        'quality': 100,
        'panoid': panoid,
        'heading': heading,
        'pitch': pitch,
        'width': width,
        'height': height,
        'from': 'PC',
        'auth': 'PSDz2ONTUDcDv5EIHUSCCWSafAOBOX80uxNEHRTBEVxt1W4931688FB2Afy9GUIsxCwxz6ZwWvvkGcuVtvvhguVtvyheuzBtyEOIxXwvCQMuHTxtFQXmE21w8wkvOAuGhrVFcEv%40vcuVtvc3CuVtvcPPuxtwf2wvOAUIuIswVHa2Dp5IC%40BvhgMuzVVtvrMhuBxLRBtIff%3DfxXwegvcguxNEHRTBBTH',
        'seckey': 'YSNoYBXRFcZK%2B2kRoOr3Ytr9QIkfl7VXc%2FZkupfasb8%3D%2CEkQ3gDtGyBiGnYmEbAfewqzVS3S5F7OJ9E20wGJo4318MZPiCt_4uPW29cbO50CIN9VOskJsTu5iPR80SPgIpPC0xgz-MiowW_XudfoltzsGJdOZtz_cNaLyibJlSVcg0AbA5foBC0X5KQCAbrwwRV7-OkgW2m87u9irYufqlvproZhrVf3xQD_g9nuWGQVl'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, headers=headers, stream=True, timeout=10)
            response.raise_for_status()  # 检查HTTP错误
            
            # 确保保存目录存在
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 保存图片
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            # print(f"图片已成功保存到: {save_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"下载失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    print(f"经过 {max_retries} 次尝试后仍未能下载图片")
    return False

class Panorama:
    def __init__(self, pano, year_month, year, month):
        self.pano = pano
        self.year_month = year_month
        self.year = year
        self.month = month

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
 
def main(csv_path,folder_out_path):
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

    # 记录信息的csv文件
    # with open(folder_out_path+r'/road_name_results.csv','w' ,newline='') as f:
    #     writer = csv.writer(f)
    # with open(folder_out_path+r'/error_data.csv','w' ,newline='') as f:
    #     writer = csv.writer(f)
    
    # df = pd.read_csv(csv_path, encoding='latin1')
    df = pd.read_csv(csv_path)
    # df['name_2'] = df['name_2'].str.encode('latin1').str.decode('utf-8')  # 尝试 latin1 → gbk

    print(df.shape)
    count = 0
    for index, row in tqdm(df.iterrows()):
        if index <= -7000:
            continue
        # if index >7000:
        #     continue
        print(df.shape[0],index)

        # 1、lat是“latitude”的缩写，纬度
        # 2、lng是“longitude”的缩写，经度
        # 中国的经纬度 经度范围:73°33′E至135°05′E。 纬度范围:3°51′N至53°33′N。
        # print(row)
        # id = row['id']
        Id = int(row['Id'])
        ORIG_FID = int(row['ORIG_FID'])
        # osm_id = row['osm_id']
        lng = row['lon']
        lat = row['lat']
        # mame_2 = row['name_2']
        
        try:
            tar_lng_lat = coord_convert(lng,lat)
            # print(tar_lng_lat)
            panoidInfos = get_panoid(tar_lng_lat[0],tar_lng_lat[1],str(lng)+'_'+str(lat), str(id),folder_out_path)
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
            # for i in range(len(filtered_panoramas)):
            for i in [0]:
                pano_id = filtered_panoramas[i].pano['ID']
                timeLine = filtered_panoramas[i].pano['TimeLine']
                # year = filtered_panoramas[i].year
                # month = filtered_panoramas[i].month

                # pic_path = folder_out_path +'/sv_degrees'  +'/'+id+'_' +str(lng)+'_' +str(lat)
                pic_path = folder_out_path +'/sv_degrees'
                if os.path.exists(pic_path) == False:
                    os.makedirs(pic_path)

                option1 = (heading + 90) % 360
                option2 = (heading - 90) % 360
                adjusted_90 = min(option1, option2)
                option3 = (adjusted_90 + 180) % 360
                option4 = (adjusted_90 - 180) % 360
                adjusted_180 = min(option3, option4)

                # for index, heading in enumerate([adjusted_90, adjusted_180]):
                    # Id_ = Id*2 + index
                for heading in [adjusted_90, adjusted_180]:
                    heading =round(heading, 1)

                    # print('heading:',heading)
                    # continue
                    # save_file_path = pic_path + '/' + str(count)+'_'+ str(id)+'_' +str(lng)+'_' +str(lat)+ '_' +timeLine+ '.jpg'
                    save_file_path = pic_path + '/' + str(Id)+'_' + str(ORIG_FID)+'_'+str(lng)+ '_'+str(lat)+ '_' + str(heading)+ '_' +timeLine+ '.jpg'
                    # save_file_path = pic_path + '/' + str(count)+'_'+ str(ORIG_FID)+ '_' +timeLine+ '.jpg'
                    # print(save_file_path,'下载完成')
                    # count+=1
                    # print('count:',count)
                    # break

                    if os.path.exists(save_file_path):
                        print(save_file_path,'已存在')
                        continue
                        # break

                    down_sv_bool = download_baidu_panorama(
                        save_path=save_file_path,
                        panoid=pano_id,
                        fovy=90,
                        heading=heading,
                        pitch=0,
                        width=1000,
                        height=500
                    )

                    if down_sv_bool:
                        print(save_file_path,'下载完成')
                        # break

        except Exception as e:
            print(f'error:{e}')
            continue
            # mistake = id + ',' + lng+','+lat + ',' + '\n'
            # with open(folder_out_path + '/error_data.csv', 'a', encoding='utf-8') as f:
            #     f.write(mistake)

coordinate_point_category = 1
# coordinate_point_category = 5
# coordinate_point_category = 6
# 分辨率 "3 - 2048*1096   4 - 4096*2048"
resolution_ratio = 4

if __name__ == '__main__':
    # 文件夹路径
    csv_path = r'd:\work\sv\single_match_files.csv'  # 需要爬取的点
    folder_out_path = r'D:\work\sv\sv_degrees01'  # 保存街景文件

    main(csv_path,folder_out_path)
