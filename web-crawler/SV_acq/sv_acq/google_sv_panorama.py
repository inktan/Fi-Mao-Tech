# -*- coding: utf-8 -*-

import csv
import time
from streetview import search_panoramas
from streetview import get_panorama
from tqdm import tqdm
from datetime import datetime  
import os
import Equirec2Perspec as E2P 
import cv2

def GSVpanoMetadataCollector(samplesFeatureClass,output_panor,output_streetviews,zoom,degree_count,height,width):
    
    if os.path.exists(output_panor) == False:
        os.makedirs(output_panor)

    if os.path.exists(output_streetviews) == False:
        os.makedirs(output_streetviews)

    with open(samplesFeatureClass, 'r') as f:  
        reader = csv.reader(f)
        mylist = list(reader)
        count = 0
        # print(mylist)
        for row in tqdm(mylist):
            count += 1
            if count == 1 or len(row)<3:
                continue
            if count >500:
                continue
            # if count <1259:
            #     continue
            
            lon = row[2]
            lat = row[3]
            
            panos = search_panoramas(lat, lon)
            if len(panos)==0:
                continue

            time.sleep(0.05)
            datas = []
            for pano in panos:
                if pano.date is not None:
                    datas.append(pano.date)
                else:
                    datas.append('2000-02')
                
            dates_as_datetime = [datetime.strptime(date, '%Y-%m') for date in datas]  
            max_date_index = dates_as_datetime.index(max(dates_as_datetime))  

            image = get_panorama(panos[max_date_index].pano_id,zoom)
            img_save_path = output_panor+f"\{row[0]}_{pano.lat}_{pano.lon}_{panos[max_date_index].date}.jpg"
            image.save(img_save_path)

            equ = E2P.Equirectangular(img_save_path)    # Load equirectangular image
            # img_save_folder = ouput+f"\{row[0]}_{pano.lat}_{pano.lon}_{panos[max_date_index].date}_degree"
            
            degree_avg = 360 / degree_count
            for i in range(degree_count):
                degree = int(i*degree_avg)
                img = equ.GetPerspective(90, degree, 0,height,width) # Specify parameters(FOV, theta, phi, height, width)
                # cv2.imwrite(img_save_folder+f'/{degree}.jpg',img)
                img_degree_save = output_streetviews+f"\{row[0]}_{pano.lat}_{pano.lon}_{panos[max_date_index].date}_{degree}.jpg"
                cv2.imwrite(img_degree_save,img)

# ------------Main Function -------------------
if __name__ == "__main__":
    
    # 输入经纬度点的csv文件
    input = r'c:\Users\wang.tan.GOA\Desktop\sv_pan\RoadPoints_50m_wgs.csv'
    # 输入街景保存文件夹
    output_panor = r'C:\Users\wang.tan.GOA\Desktop\sv_pan\sv_pan02'
    output_streetviews = r'C:\Users\wang.tan.GOA\Desktop\sv_pan\sv_pan02'
    # 全景分辨率设置 1-512*1024; 2-1024*2048; 3-2048*4096; 4-4096*8192
    zoom = 2
    # 角度个数
    degree_count = 4
    # 角度街景高度
    height = 720
    # 角度街景宽度
    width = 960
    
    GSVpanoMetadataCollector(input,output_panor,output_streetviews,zoom,degree_count,height,width)



