# -*- coding: utf-8 -*-

import csv
import time
from streetview import search_panoramas,get_panorama,get_degree_streetview
from tqdm import tqdm
import os
import numpy as np
import pandas as pd  
import json

def GSVpanoMetadataCollector(input_csv,output_):
  
    data05 = {}
    file_path = r'd:\BaiduNetdiskDownload\roadpoints_50m\id_panoramas_infos_02.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data05 = json.load(file)

    number_of_elements = len(data05)
    df = pd.read_csv(input_csv)

    for index, key in enumerate(sorted(data05)):
        
        if index <= 268000:
            continue
        # if index >16000:
        #     continue

        panos = data05[key]
        
        if len(panos)==0:
            continue

        print(f"排序后索引: {index}, 键: {key}, 总数: {number_of_elements}")
                
        filtered_df = df.loc[df['PointID'] == int(key)]
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
                for degree in [0,90,180,270]:
                    image = get_degree_streetview(pano['pano_id'],degree)
                    img_save_path = output_floder+f"/pan00_{pano['date_year_month']}_{degree}.jpg"

                    svPanoImgs[img_save_path] = image
                sv_infos.append([pano['pano_id'], pano['heading'], pano['pitch'], pano['date_year_month']])
                break

            except:
                continue
        # 无街景
        if len(svPanoImgs) == 0:
            continue
        # 条件2：获取2013-2008年份的街景

        years = [item.get("year", None) for item in sorted_pans]

        years_set = set(years)  
        all_0 = len(set(years_set)) == 1 and list(set(years_set))[0] == 0  

        if all_0:
            try :
                for degree in [0,90,180,270]:
                    image = get_degree_streetview(sorted_pans[-1]['pano_id'],degree)
                    img_save_path = output_floder+f"/pan01_{pano['date_year_month']}_{degree}.jpg"

                    svPanoImgs[img_save_path] = image
                sv_infos.append([pano['pano_id'], pano['heading'], pano['pitch'], pano['date_year_month']])
                # break
            except:
                a=0
                # continue
        else:
            for pano in sorted_pans:
                if pano['year'] <= 2013:
                # if 2008 <= pano['year'] and pano['year'] <= 2013:
                    try :
                        for degree in [0,90,180,270]:
                            image = get_degree_streetview(pano['pano_id'],degree)
                            img_save_path = output_floder+f"/pan01_{pano['date_year_month']}_{degree}.jpg"

                            svPanoImgs[img_save_path] = image
                        sv_infos.append([pano['pano_id'], pano['heading'], pano['pitch'], pano['date_year_month']])
                        break
                    except:
                        continue

        for key,value in svPanoImgs.items():
            value.save(key)
        output_csv = output_ +  f"\{id}_{lon}_{lat}\\panos_info.csv" 
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
    input_csv = r'd:\BaiduNetdiskDownload\roadpoints_50m\RoadPoints_50m_unique.csv'
    # 输入街景保存文件夹
    output_ = r'E:\work\sv_chenlong20240907\sv_pan'
    output_ = r'D:\BaiduNetdiskDownload\roadpoints_50m\sv_pan'
    
    if os.path.exists(output_) == False:
        os.makedirs(output_)    
    GSVpanoMetadataCollector(input_csv,output_)


