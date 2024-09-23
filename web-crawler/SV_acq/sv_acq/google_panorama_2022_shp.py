# -*- coding: utf-8 -*-

import csv
import time
from streetview import search_panoramas
from streetview import get_panorama
from tqdm import tqdm
import geopandas as gpd
import os

class Panorama:
    def __init__(self, pano, year_month, year, month):
        self.pano = pano
        self.year_month = year_month
        self.year = year
        self.month = month

def GSVpanoMetadataCollector(shp_path,output_,zoom):
    gdf_point = gpd.read_file(shp_path)
    for index,point in  enumerate(tqdm(gdf_point['geometry'])):

        # if index >3005:
        #     continue
        # if index <= 1689:
        #     continue
        lon = point.x
        lat = point.y

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
                panoramas.append(Panorama(pano, int(data[0])+int(data[1])/12, int(data[0]), int(data[1])/12))
            else:
                panoramas.append(Panorama(pano, 0, 0, 0))

        sorted_panoramas = sorted(panoramas, key=lambda x: x.year_month, reverse=True)

        for pano_year in sorted_panoramas:
            time.sleep(0.05)
            try :
                # if pano_year.year < 2009:
                #     continue
                
                pano = pano_year.pano

                image = get_panorama(pano.pano_id,zoom)
                img_save_path = output_+f"/{gdf_point['id'][index]}_{lon}_{lat}_{pano.date}.jpg"
                # img_save_path = output_ + f"/{row[0]}_{row[1]}_{row[2]}.jpg"
                image.save(img_save_path)
                break
                # name_count += 1
            except:
                continue
                
# ------------Main Function -------------------
if __name__ == "__main__":
    
    # 输入经纬度点的csv文件
    input = r'F:\sv_yj\point_degree\point_degree.shp'
    # 输入街景保存文件夹
    output_ = r'F:\sv_yj\sv_yj_'
    # 全景分辨率设置 1-512*1024; 2-1024*2048; 3-2048*4096; 4-4096*8192
    zoom = 3
    if os.path.exists(output_) == False:
        os.makedirs(output_)    
    GSVpanoMetadataCollector(input,output_,zoom)



