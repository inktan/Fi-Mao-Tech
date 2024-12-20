# -*- coding: utf-8 -*-

import csv
import time
from streetview import search_panoramas
from streetview import get_panorama
from tqdm import tqdm
import os
import numpy as np
import pandas as pd  
import json

def GSVpanoMetadataCollector(input_csv,output_,zoom):
  
    data05 = {}
    file_path = r'e:\work\roadpoints_50m\id_panoramas_infos_02.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data05 = json.load(file)

    number_of_elements = len(data05)
    df = pd.read_csv(input_csv)
    all_points_count = df.shape[0]

    for index, key in enumerate(sorted(data05)):
        
        if index <= 89:
            continue
        # if index >16000:
        #     continue

        panos = data05[key]
        
        if len(panos)==0:
            continue

        print(f"排序后索引: {index}, 键: {key}, 总数: {number_of_elements}")
                
        filtered_df = df.loc[df['PointID'] == key]
        id = key
        lon = filtered_df.iloc[0,2]
        lat = filtered_df.iloc[0,3]
        
        output_floder = output_ +  f"\{id}_{lon}_{lat}" 
        if os.path.exists(output_floder) == False:
            os.makedirs(output_floder)

        # sorted_pans = sorted(panos, key=lambda pan: int(pan.date.split('-')[0]) if pan.date is not None and '-' in pan.date else 0, reverse=True)
        sorted_pans = sorted(panos, key=lambda x: x.get('year_month', float('-inf')), reverse=True) 
        # print(sorted_pans)
        # filtered_pans = [pano for pano in panos if pano.date is not None]
        
        svPanoImgs = {}
        sv_infos = []
        # 条件1：获取最新年份的街景
        for pano in sorted_pans:
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
                    img_save_path = output_floder+f"/pan00_{pano.date}.jpg"
                    svPanoImgs[img_save_path] = image
                    sv_infos.append([pano.pano_id, pano.heading, pano.pitch, pano.date])
                    break
            except:
                continue
        # 无街景
        if len(svPanoImgs) == 0:
            continue
        # 条件2：获取2013-2008年份的街景
        for pano in sorted_pans:
            if 2008 <= int(pano.date.split('-')[0]) and int(pano.date.split('-')[0]) <= 2013:
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
                        img_save_path = output_floder+f"/pan01_{pano.date}.jpg"
                        svPanoImgs[img_save_path] = image
                        sv_infos.append([pano.pano_id, pano.heading, pano.pitch, pano.date])
                        break
                except:
                    continue

        for key,value in svPanoImgs.items():
            value.save(key)
        output_csv = output_ +  f"\{id}_{lon}_{lat}\\pans_info.csv" 
        with open(output_csv ,'w' ,newline='') as f: 
            writer = csv.writer(f)
            writer.writerow(['pano_id','heading','pitch','date'])
        with open(output_csv ,'a' ,newline='') as f: 
            writer = csv.writer(f)
            writer.writerows(sv_infos)


# ------------Main Function -------------------
if __name__ == "__main__":
    
    # 输入经纬度点的csv文件
    input_csv = r'e:\work\sv_chenlong20240907\RoadPoints_50m_unique.csv'
    input_csv = r'e:\work\roadpoints_50m\RoadPoints_50m_unique.csv'
    # 输入街景保存文件夹
    output_ = r'E:\work\sv_chenlong20240907\sv_pan'
    output_ = r'E:\work\roadpoints_50m\sv_pan'
    
    # 全景分辨率设置 1-512*1024; 2-1024*2048; 3-2048*4096; 4-4096*8192
    zoom = 2
    if os.path.exists(output_) == False:
        os.makedirs(output_)    
    GSVpanoMetadataCollector(input_csv,output_,zoom)


