# -*- coding: utf-8 -*-

import csv
import time
from streetview import search_panoramas
from streetview import get_panorama
from tqdm import tqdm
import os
import numpy as np
import pandas as pd  

class Panorama:
    def __init__(self, pano,heading, year_month, year, month):
        self.pano = pano
        self.heading = heading
        self.year_month = year_month
        self.year = year
        self.month = month

def GSVpanoMetadataCollector(input_csv,output_,zoom,output_csv):
  
    df = pd.read_csv(input_csv)  
    all_points_count = df.shape[0]
    for index, row in tqdm(df.iterrows()):
        print(index,all_points_count)
        
        # if index <= 12485:
        #     continue
        # if index >16000:
        #     continue
        
        id = row[0]
        lon = row[3]
        lat = row[4]
        
        output_floder = output_+  f"\{id}_{lon}_{lat}" 
        if os.path.exists(output_floder) == True:
            continue

        panos = []
        try:
            panos = search_panoramas(lat, lon)
        except:
            continue

        if len(panos)==0:
            continue
        
        panoramas = []
        for pano in panos:
            if pano.date is not None:
                data = pano.date.split('-')
                panoramas.append(Panorama(pano,pano.heading, int(data[0])+int(data[1])/12.0,data[0], int(data[1])/12))
            else:
                panoramas.append(Panorama(pano,pano.heading,  0, 0, 0))

        sorted_panoramas = sorted(panoramas, key=lambda x: x.year_month, reverse=True)

        output_floder = output_+  f"\{id}_{lon}_{lat}" 
        if os.path.exists(output_floder) == False:
            os.makedirs(output_floder)
        else:
            continue

        # name_count = 0
        for pano_year in sorted_panoramas:
            time.sleep(0.05)
            try :
                # if pano_year.year < 2009:
                #     continue
                # if '2016' in pano.date or  '2018' in pano.date or  '2021' in pano.date or  '2022' in pano.date or  '2023' in pano.date :
                #     continue
                
                image = get_panorama(pano_year.pano.pano_id,zoom)
                img_array = np.array(image)
                # 判断黑色像素
                # 对于RGB图像，黑色像素的值为(0, 0, 0)
                # 对于灰度图像，黑色像素的值为0
                if len(img_array.shape) == 3:  # RGB图像
                    black_pixels = (img_array == [0, 0, 0]).all(axis=2)
                else:  # 灰度图像
                    black_pixels = (img_array == 0)

                num_black_pixels = np.sum(black_pixels)
                total_pixels = img_array.size // 3 if len(img_array.shape) == 3 else img_array.size

                black_pixel_ratio = num_black_pixels / total_pixels
                # 判断黑色像素比例是否大于0.28
                # if black_pixel_ratio > 0.12:
                #     continue
                # else:
                img_save_path = output_floder+f"/{name_count}_{pano_year.pano.date}.jpg"
                image.save(img_save_path)
                    
                    # with open(output_csv ,'a' ,newline='') as f: 
                    #     writer = csv.writer(f)
                    #     writer.writerow([id,name_count,pano_year.heading])
                    
                # name_count += 1
                break
                    
            except Exception as e :
                print(f'error:{e}')
                continue
                
# ------------Main Function -------------------
if __name__ == "__main__":
    
    # 输入经纬度点的csv文件
    input_csv = r'e:\work\sv_j_ran\20241227\data_coor_unique_500_circle.csv'
    # 输入街景保存文件夹
    output_ = r'e:\work\sv_j_ran\20241227\sv_pan'
    
    zoom = 2
    if os.path.exists(output_) == False:
        os.makedirs(output_)    
    GSVpanoMetadataCollector(input_csv,output_,zoom,'output_csv')


