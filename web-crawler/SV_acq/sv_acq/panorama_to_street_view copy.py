# -*- coding: utf-8 -*-

import csv
# import time
# from streetview import search_panoramas
# from streetview import get_panorama
# from datetime import datetime  
import os
import Equirec2Perspec as E2P 
import cv2
import os  
from tqdm import tqdm
from PIL import Image  
import numpy as np  

input = r'c:\Users\wang.tan.GOA\Desktop\sv_pan\sv_test_info.csv'
output_ = r'C:\Users\wang.tan.GOA\Desktop\sv_pan\sv_pan02'

# fov是镜头的远近关系 水平方向范围，范围[10,360]，fov=360即可显示整幅全是图
# pitch是仰头，低头关系 垂直视角，范围[0,90]。
# heading是东南西北旋转关系 水平视角，范围[0.360]
fov = 90
phi = 0

# 角度个数
degree_count = 4
    
# 角度街景宽度
width = 640
height = 640

with open(input, 'r') as f:  
    reader = csv.reader(f)
    mylist = list(reader)
    count = 0
    # print(mylist)
    for row in tqdm(mylist):
        count += 1
        if count == 1 or len(row)<3:
            continue
        # if count >300000005:
        #     continue
        # if count <= 16890:
        #     continue
        # lon = row[5]
        # lat = row[6]
        
        image_path = output_+f"/{row[0]}.jpg"

        # 判断文件夹路径是否存在
        if os.path.exists(image_path):
            # print(f'文件夹路径 {image_path} 存在。')
        # else:
        #     print(f'文件夹路径 {img_save_path} 不存在。')

            equ = E2P.Equirectangular(image_path)    # Load equirectangular image

            # degree_avg = 360 / degree_count
            # degrees = [i*degree_avg for i in range(degree_count)]
            num =float(row[1])
            degrees = [(num + 0) % 360,
                        (num + 90) % 360,
                        (num + 180) % 360,
                        (num + 270) % 360,]
            # fov = row[9]
            # fov = row[7]
            
            image_type = image_path.split('.')[-1]
            for i in degrees:
                img = equ.GetPerspective(float(fov),float(i), phi,height,width) # Specify parameters(FOV, theta, phi, height, width)
                persp_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  
                pil_image = Image.fromarray(persp_rgb)  

                img_degree_save = image_path.replace('sv_pan000000','sv_test_fov90').replace('.'+image_type,'_'+str(i)+'_'+str(fov)+'.'+image_type)
                folder_path = os.path.dirname(img_degree_save)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                pil_image.save(img_degree_save)  # 可以保存为.jpg、.png等格式
                # cv2.imwrite(img_degree_save,img)


