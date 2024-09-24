# -*- coding: utf-8 -*-

import csv
import time
from streetview import search_panoramas,get_panorama,get_degree_streetview
from tqdm import tqdm
import os
import numpy as np
import pandas as pd  
import json

class Panorama:
    def __init__(self, pano,heading, year_month, year, month):
        self.pano = pano
        self.heading = heading
        self.year_month = year_month
        self.year = year
        self.month = month

def GSVpanoMetadataCollector(input_csv,output_):
    
    df = pd.read_csv(input_csv)  
    for index, row in tqdm(df.iterrows()):
        
        # if index <= 15000:
        #     continue
        # if index >16000:
        #     continue
        
        id = row[0]
        id_01 = row[2]
        lon = row[3]
        lat = row[4]

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

        # output_floder = output_+  f"\{id}_{id_01}_{lon}_{lat}" 
        # if os.path.exists(output_floder) == False:
        #     os.makedirs(output_floder)

        for pano_item in sorted_panoramas:
            try :
                for degree in [0,90,180,270]:
                    image = get_degree_streetview(pano_item.pano.pano_id,degree)
                    img_save_path = output_ +f'\{id}_{id_01}_{lon}_{pano_item.pano.date}_{degree}.jpg'
                    image.save(img_save_path)
                break
            except:
                continue
    

# ------------Main Function -------------------
if __name__ == "__main__":
    
    # 输入经纬度点的csv文件
    input_csv = r'e:\work\sv_YJ_20240924\points.csv'
    # 输入街景保存文件夹
    output_ = r'e:\work\sv_YJ_20240924\sv_degrees'
    if os.path.exists(output_) == False:
        os.makedirs(output_)    

    GSVpanoMetadataCollector(input_csv,output_)


