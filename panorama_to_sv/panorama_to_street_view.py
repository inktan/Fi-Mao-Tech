# -*- coding: utf-8 -*-

import os
import Equirec2Perspec as E2P 
import cv2
import os  
from tqdm import tqdm
from PIL import Image  
import numpy as np  

def panorama_to_street_view(input_dir,fov,degree_count,phi,height,width):
      
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

    for i,image_path in enumerate(tqdm(img_paths,total=len(img_paths))): 
        # 判断文件是否为图片类型  
        if image_path.lower().endswith(image_types):
            # if i < 26400:
            #     continue
            # if i >= 330000:
            #     continue
            try:
                
                equ = E2P.Equirectangular(image_path)    # Load equirectangular image

                degree_avg = 360 / degree_count
                degrees = [i*degree_avg for i in range(degree_count)]
                # degrees = [0,180]
                
                image_type = image_path.split('.')[-1]
                for i in degrees:
                    # img_degree_save = image_path.replace('svi',f'街景_{width}_{height}').replace('.'+image_type,'_'+str(int(i))+'.'+image_type)
                    img_degree_save = image_path.replace('全景',f'街景').replace('.'+image_type,'_'+str(int(i))+'.'+image_type)
                    # img_degree_save = image_path.replace('sv_pan_zoom3',f'街景_{width}_{height}').replace('.'+image_type,'_'+str(int(i))+'.'+image_type)
                    # img_degree_save = image_path.replace(r'F:\GoogleDrive\wt282532\我的云端硬盘',r'F:\work\sv_ran\sv_degrees').replace('.'+image_type,'_'+str(int(i))+'.'+image_type)
                    # img_degree_save = image_path.replace(r'F:\GoogleDrive\wt282532\我的云端硬盘',r'F:\work\sv_ran\sv_degrees').replace('.'+image_type,'_'+str(int(i))+'.'+image_type)
                    if os.path.exists(img_degree_save):
                        continue

                    img = equ.GetPerspective(fov, i, phi,height,width) # Specify parameters(FOV, theta, phi, height, width)
                    persp_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(persp_rgb)

                    folder_path = os.path.dirname(img_degree_save)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    pil_image.save(img_degree_save)  # 可以保存为.jpg、.png等格式
                    # cv2.imwrite(img_degree_save,img)
           
            except Exception as e:
                print(e)

# ------------Main Function -------------------
if __name__ == "__main__":
    input = r'E:\work\sv_npc\全景'
    
    # fov是镜头的远近关系 水平方向范围，范围[10,360]，fov=360即可显示整幅全是图
    # pitch是仰头，低头关系 垂直视角，范围[0,90]。
    # heading是东南西北旋转关系 水平视角，范围[0.360]
    # fov = 120
    # fov = 105
    fov = 90
    # fov = 75
    # fov = 60
    # fov = 45
    phi = 0
    # phi = 6

    # 角度个数
    degree_count = 4

    # 角度街景宽度
    # width = 960 # 240*4
    # height = 720 # 240*3
    # width = 1920 # 240*4*2
    # height = 1440 # 240*3*2
    # width = 3000
    # height = 2250
    # width = 1000
    # height = 1000
    width = 2048
    height = 1536

    panorama_to_street_view(input ,fov,degree_count,phi,height,width)
    