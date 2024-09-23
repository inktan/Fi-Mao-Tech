# -*- coding: utf-8 -*-

# import csv
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
import geopandas as gpd

def panorama_to_street_view(input_dir,fov,degree_count,phi,height,width):
    # 输入经纬度点的csv文件
    shp_path = r'F:\sv_yj\point_degree\point_degree.shp'
    gdf_point = gpd.read_file(shp_path)
    # for index,point in  enumerate(tqdm(gdf_point['id'])):
    #     print(index,point)

    # 定义图片文件类型  
    image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')  
        
    # 遍历输入文件夹中的所有图片文件，并进行处理
    img_paths = []
    roots = []
    img_names = []

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)
                roots.append(root)

    for i,image_path in enumerate(tqdm(img_paths)): 
        # 判断文件是否为图片类型  
        if image_path.lower().endswith(image_types):
            # if i<14390:
            #     continue
            try:
                equ = E2P.Equirectangular(image_path)    # Load equirectangular image

                img_name = img_names[i]
                image_type = image_path.split('.')[-1]

                degree_avg = 360 / degree_count
                degrees = [i*degree_avg for i in range(degree_count)]
                # degrees = [90,270]

                # index = img_name.split('_')[0]
                # degree_01 = gdf_point['angle_02_'][int(index)]
                # degree_02 = gdf_point['angle_01_'][int(index)]

                # degrees = [float(degree_01),float(degree_02)]
                for i in degrees:
                    img = equ.GetPerspective(fov, i, phi,height,width) # Specify parameters(FOV, theta, phi, height, width)
                    persp_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  
                    pil_image = Image.fromarray(persp_rgb)  

                    out_dir = input_dir.replace('sv_pan02','sv_pan02_640_640')
                    img_name_ = img_name.replace('.'+image_type,'_'+str(int(i))+'.'+image_type)
                    img_degree_save = out_dir+'\\'+img_name_
                    folder_path = os.path.dirname(img_degree_save)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    pil_image.save(img_degree_save)  # 可以保存为.jpg、.png等格式
                    # cv2.imwrite(img_degree_save,img)
            except Exception as e:
                print(e)

# ------------Main Function -------------------
if __name__ == "__main__":
    input = r'C:\Users\wang.tan.GOA\Desktop\sv_pan\sv_pan02'

    # fov是镜头的远近关系 水平方向范围，范围[10,360]，fov=360即可显示整幅全是图
    # pitch是仰头，低头关系 垂直视角，范围[0,90]。
    # heading是东南西北旋转关系 水平视角，范围[0.360]
    fov = 100
    phi = 0

    # 角度个数
    degree_count = 4
        
    # 角度街景宽度
    width = 640
    height = 640
    
    panorama_to_street_view(input ,fov,degree_count,phi,height,width)

