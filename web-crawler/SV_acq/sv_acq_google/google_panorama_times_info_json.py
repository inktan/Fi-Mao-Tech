# -*- coding: utf-8 -*-
import csv
import time
from streetview import search_panoramas
from tqdm import tqdm
import os
import numpy as np
import json
import pandas as pd

def GSVpanoMetadataCollector():
    
    # 读取CSV文件，并保存'lat'和'lon'同时不重复的列数据
    # df_unique = pd.read_csv(input_csv).drop_duplicates(subset=['long', 'lat'])
    # print(df_unique.shape)
    # csv_file = r'e:\work\sv_j_ran\sv_google_20240903\data_coor_unique.csv'
    # df_unique.to_csv(csv_file, index=False)
    
    json_dict={}
    with open(input_csv, 'r') as f:  
        reader = csv.reader(f)
        mylist = list(reader)
        count = 0
        # print(mylist)
        for row in tqdm(mylist):
            count += 1
            if count == 1 or len(row)<3:
                continue
            # if count > 55000:
            #     continue
            # if count > 100 :
            #     continue
            
            id = row[0]
            lon = row[2]
            lat = row[1]
        
            panos = []
            try:
                panos = search_panoramas(lat, lon)
                
            except Exception as e :
                print(f'error:{e}')
                continue

            panoramas_info = []
            for pano in panos:
                pand_info={}
                if pano.date is not None:
                    data = pano.date.split('-')
                    
                    pand_info['pano_id']=pano.pano_id
                    pand_info['heading']=pano.heading
                    pand_info['pitch']=pano.pitch
                    pand_info['date_year_month']=data[0]+'_'+data[1]
                    pand_info['year_month']=int(data[0])+int(data[1])/12.0
                    pand_info['year']=int(data[0])
                    pand_info['month']=int(data[1])/12
                    
                    panoramas_info.append(pand_info)
                else:
                    # 使用列表推导式和 any() 函数来判断列表中是否包含特定的键值对
                    key_to_check = 'date_year_month'
                    value_to_check = ''
                    contains_key_value_pair = any(d[key_to_check] == value_to_check for d in panoramas_info if key_to_check in d)

                    if not contains_key_value_pair:
                        pand_info['pano_id']=pano.pano_id
                        pand_info['heading']=pano.heading
                        pand_info['pitch']=pano.pitch
                        pand_info['date_year_month']=''
                        pand_info['year_month']=0
                        pand_info['year']=0
                        pand_info['month']=0
                            
                        panoramas_info.append(pand_info)
            json_dict[id] = panoramas_info
            
            if count%1000==0:
                with open(json_file_path, 'w', encoding='utf-8') as file:
                    json.dump(json_dict, file, ensure_ascii=False, indent=4)

    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(json_dict, file, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    # 输入经纬度点的csv文件
    input_csv = r'e:\work\sv_yantu\points.csv'
    # 输入街景保存文件夹
    json_file_path = r'e:\work\sv_yantu\data_coor_id_panoramas_infos.json'
    
    GSVpanoMetadataCollector()
