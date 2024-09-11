# -*- coding: utf-8 -*-

import csv
import time
from streetview import search_panoramas
from streetview import get_panorama
from tqdm import tqdm
import os
import numpy as np
import pandas as pd  

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
        lon = row[2]
        lat = row[3]
        
        panos = []
        try:
            panos = search_panoramas(lat, lon)
        except:
            continue

        if len(panos)==0:
            continue
        
        output_floder = output_ +  f"\{id}_{lon}_{lat}" 
        if os.path.exists(output_floder) == False:
            os.makedirs(output_floder)

        output_csv = output_ +  f"\{id}_{lon}_{lat}\\pans_info.csv" 
        with open(output_csv ,'w' ,newline='') as f: 
            writer = csv.writer(f)
            writer.writerow(['pan_id','heading','pitch','date_year_month','year_month','year','month'])

        sorted_pans = sorted(pans, key=lambda x: int(x.data))  

        print(sorted_pans)
        break

        for pano in panos:
            if pano.data[0]==2012:
                try :
                    image = get_panorama(pano.pano_id,zoom)
                    img_array = np.array(image)
                    if len(img_array.shape) == 3:
                        black_pixels = (img_array == [0, 0, 0]).all(axis=2)
                    else:
                        black_pixels = (img_array == 0)

                    num_black_pixels = np.sum(black_pixels)
                    total_pixels = img_array.size // 3 if len(img_array.shape) == 3 else img_array.size

                    black_pixel_ratio = num_black_pixels / total_pixels
                    # 判断黑色像素比例是否大于0.28
                    if black_pixel_ratio > 0.12:
                        continue
                    else:
                        img_save_path = output_floder+f"/{pano.data[0]}.jpg"
                        image.save(img_save_path)
                        with open(output_csv ,'a' ,newline='') as f: 
                            writer = csv.writer(f)
                            writer.writerow([id, pano.heading, pano.pitch, int(pano.data[0])+int(pano.data[1])/12.0, pano.data[0], int(pano.data[1])/12.0])
                    break

            elif pano.data[0]==2011:
                try :
                    image = get_panorama(pano.pano_id,zoom)
                    img_array = np.array(image)
                    if len(img_array.shape) == 3:
                        black_pixels = (img_array == [0, 0, 0]).all(axis=2)
                    else:
                        black_pixels = (img_array == 0)

                    num_black_pixels = np.sum(black_pixels)
                    total_pixels = img_array.size // 3 if len(img_array.shape) == 3 else img_array.size

                    black_pixel_ratio = num_black_pixels / total_pixels
                    # 判断黑色像素比例是否大于0.28
                    if black_pixel_ratio > 0.12:
                        continue
                    else:
                        img_save_path = output_floder+f"/{pano.data[0]}.jpg"
                        image.save(img_save_path)
                        with open(output_csv ,'a' ,newline='') as f: 
                            writer = csv.writer(f)
                            writer.writerow([id, pano.heading, pano.pitch, int(pano.data[0])+int(pano.data[1])/12.0, pano.data[0], int(pano.data[1])/12.0])
                    break

        for pano in panos:
            if pano.data[0]==2022:
                try :
                    image = get_panorama(pano.pano_id,zoom)
                    img_array = np.array(image)
                    if len(img_array.shape) == 3:
                        black_pixels = (img_array == [0, 0, 0]).all(axis=2)
                    else:
                        black_pixels = (img_array == 0)

                    num_black_pixels = np.sum(black_pixels)
                    total_pixels = img_array.size // 3 if len(img_array.shape) == 3 else img_array.size

                    black_pixel_ratio = num_black_pixels / total_pixels
                    # 判断黑色像素比例是否大于0.28
                    if black_pixel_ratio > 0.12:
                        continue
                    else:
                        img_save_path = output_floder+f"/{pano.data[0]}.jpg"
                        image.save(img_save_path)
                        with open(output_csv ,'a' ,newline='') as f: 
                            writer = csv.writer(f)
                            writer.writerow([id, pano.heading, pano.pitch, int(pano.data[0])+int(pano.data[1])/12.0, pano.data[0], int(pano.data[1])/12.0])
                    break

            elif pano.data[0]==2023:
                try :
                    image = get_panorama(pano.pano_id,zoom)
                    img_array = np.array(image)
                    if len(img_array.shape) == 3:
                        black_pixels = (img_array == [0, 0, 0]).all(axis=2)
                    else:
                        black_pixels = (img_array == 0)

                    num_black_pixels = np.sum(black_pixels)
                    total_pixels = img_array.size // 3 if len(img_array.shape) == 3 else img_array.size

                    black_pixel_ratio = num_black_pixels / total_pixels
                    # 判断黑色像素比例是否大于0.28
                    if black_pixel_ratio > 0.12:
                        continue
                    else:
                        img_save_path = output_floder+f"/{pano.data[0]}.jpg"
                        image.save(img_save_path)
                        with open(output_csv ,'a' ,newline='') as f: 
                            writer = csv.writer(f)
                            writer.writerow([id, pano.heading, pano.pitch, int(pano.data[0])+int(pano.data[1])/12.0, pano.data[0], int(pano.data[1])/12.0])
                    break


# ------------Main Function -------------------
if __name__ == "__main__":
    
    # 输入经纬度点的csv文件
    input_csv = r'e:\work\sv_chenlong20240907\RoadPoints_50m_unique.csv'
    # 输入街景保存文件夹
    output_ = r'E:\work\sv_chenlong20240907\sv_pan'
    
    # 全景分辨率设置 1-512*1024; 2-1024*2048; 3-2048*4096; 4-4096*8192
    zoom = 2
    if os.path.exists(output_) == False:
        os.makedirs(output_)    
    GSVpanoMetadataCollector(input_csv,output_,zoom,output_csv)


