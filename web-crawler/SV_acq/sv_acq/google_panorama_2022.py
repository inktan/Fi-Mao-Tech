# -*- coding: utf-8 -*-

import csv
import time
from streetview import search_panoramas
from streetview import get_panorama
from tqdm import tqdm
import os
import numpy as np

class Panorama:
    def __init__(self, pano,heading, year_month, year, month):
        self.pano = pano
        self.heading = heading
        self.year_month = year_month
        self.year = year
        self.month = month

def GSVpanoMetadataCollector(samplesFeatureClass,output_,zoom,output_csv):

    with open(samplesFeatureClass, 'r') as f:  
        reader = csv.reader(f)
        mylist = list(reader)
        count = 0
        # print(mylist)
        for row in tqdm(mylist):
            count += 1
            if count == 1 or len(row)<3:
                continue
            # if count <= 16890:
            #     continue
            # if count >300000005:
            #     continue
            lon = row[2]
            lat = row[3]
            
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

            for pano_year in sorted_panoramas:
                time.sleep(0.05)
                try :
                    # if pano_year.year < 2009:
                    #     continue
                    
                    pano = pano_year.pano

                    image = get_panorama(pano.pano_id,zoom)
                    # img_save_path = output_+f"/{row[0]}_{row[1]}_{row[2]}_{pano.date}.jpg"
                    img_save_path = output_+f"/{row[0]}_{row[2]}_{row[3]}.jpg"
                    # img_save_path = output_ + f"/{row[0]}.jpg"
                    # image.save(img_save_path)
                    
                    # image = Image.open(image_path)
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
                    if black_pixel_ratio > 0.28:
                        continue
                    else:
                        image.save(img_save_path)
                        
                        with open(output_csv ,'a' ,newline='') as f: 
                            writer = csv.writer(f)
                            writer.writerow([f"{row[0]}_{row[2]}_{row[3]}",pano_year.heading,row[2],row[3]])
                        break
                    # break
                    # name_count += 1
                except Exception as e :
                    print(f'error:{e}')
                    continue
                
# ------------Main Function -------------------
if __name__ == "__main__":
    
    # 输入经纬度点的csv文件
    input = r'c:\Users\wang.tan.GOA\Desktop\sv_pan\RoadPoints_50m_wgs.csv'
    # 输入街景保存文件夹
    output_ = r'C:\Users\wang.tan.GOA\Desktop\sv_pan\sv_pan02'
    output_csv = r'c:\Users\wang.tan.GOA\Desktop\sv_pan\sv_test_info.csv'
    
    with open(output_csv ,'w' ,newline='') as f: 
        writer = csv.writer(f)
        # writer.writerow(['id','heading_google','lat','lon','heading','pitch','fov1','fov2'])
        writer.writerow(['id','heading_google','lat','lon','heading','pitch'])
    # 全景分辨率设置 1-512*1024; 2-1024*2048; 3-2048*4096; 4-4096*8192
    zoom = 2
    if os.path.exists(output_) == False:
        os.makedirs(output_)    
    GSVpanoMetadataCollector(input,output_,zoom,output_csv)



