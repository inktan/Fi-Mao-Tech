# -*- coding: utf-8 -*-

import time
import time
from tqdm import tqdm
import os
import pandas as pd  
import time
from streetview import get_panorama

def GSVpanoMetadataCollector(input_csv,output_,zoom):
  
    df = pd.read_csv(input_csv)  
    all_points_count = df.shape[0]
    for index, row in tqdm(df.iterrows()):
        print(index,all_points_count)
        
        # if index <= 6612:
        #     continue
        # if index >16000:
        #     continue

        id = int(row[0])	
        longitude = float(row[1])	
        latitude = float(row[2])	
        panoid = row[3]	
        year = row[4]	
        month = row[5]

        time.sleep(0.05)
        try :
            img_save_path = output_+f"/{int(id)}_{longitude}_{latitude}_{year}_{month}.png"
            if os.path.exists(img_save_path):
                continue
            print(img_save_path)
            image = get_panorama(panoid,zoom)
            image.save(img_save_path)
            print(img_save_path,'下载完成')
                
            break
                
        except Exception as e :
            print(f'error:{e}')
            continue
                
# ------------Main Function -------------------
# googlemap中点状区域的街景获取
if __name__ == "__main__":
    
    # 输入经纬度点的csv文件
    input_csv = r'D:\BaiduNetdiskDownload\work\merged_coordinates_01_sv_infos_.csv'
    # 输入街景保存文件夹
        
    # 全景分辨率设置 1-512*1024; 2-1024*2048; 3-2048*4096; 4-4096*8192
    # 全景分辨率设置 1-512*1024; 2-7++*1536; 3-1024*3072; 4-2048*4096; 5-4096*8192
    zoom = 3
    output_ =r'D:\BaiduNetdiskDownload\work\sv_pan_zoom'+str(zoom)

    if os.path.exists(output_) == False:
        os.makedirs(output_)    

    GSVpanoMetadataCollector(input_csv,output_,zoom)


