# -*- coding: utf-8 -*-

import os, scipy.io
import numpy as np
from PIL import Image
from tqdm import tqdm
import numpy as np  
from PIL import Image  
import os
from tqdm import tqdm

def extracted_arch(img_paths,img_names,extracted_ss_folder,extracted_sv_folder):
    for i,img_path in enumerate(tqdm(img_paths)):

        rgb_image = Image.open(img_path)  
        # 获取图像的宽度和高度  
        width, height = rgb_image.size  
        # 计算总像素数量  
        total_pixels = width * height  
        # 如果像素数量大于指定的最大值，进行缩放  
        max_pixels = 1000000 # 4g显存可以跑4000000
        if total_pixels > max_pixels:  
            # 计算缩放比例  
            scale = (max_pixels / total_pixels) ** 0.5  
            # 计算新的宽度和高度  
            new_width = int(width * scale)  
            new_height = int(height * scale)  
            # 创建一个新的缩放后的图像  
            rgb_image = rgb_image.resize((new_width, new_height))
            
        # 加载灰度图和RGB色彩图
        if ".jpg" in img_path:
            img_path = img_path.replace(".jpg",".png")
        elif ".jpeg" in img_path:
            img_path = img_path.replace(".jpeg",".png")

        ss_rgb_path = img_path.replace('svi_pan03','ade_20k\\ade_20k_语义分析_色块图')
        ss_pil_image = Image.open(ss_rgb_path)
        # 将图像转换为NumPy数组  
        ss_rgb_array = np.array(ss_pil_image)
        # 创建一个全零数组，用于存放提取的像素
        # 创建一个全为白色的图像数组
        white_ss_array = np.ones_like(ss_rgb_array) * 255
        white_sv_array = np.ones_like(ss_rgb_array) * 255
        rgb_array = np.array(rgb_image)  
        # 遍历颜色列表中的每种颜色
        for color in color_list:
            # 创建一个布尔掩码，其中与当前颜色匹配的像素为True
            mask = (ss_rgb_array == color).all(axis=2)
            # 将匹配的像素保留为其原始颜色，不匹配的像素设置为白色
            white_ss_array[mask] = ss_rgb_array[mask]
            white_sv_array[mask] = rgb_array[mask]
      
        # 将修改后的数组转换回图像
        ss_result_image = Image.fromarray(white_ss_array.astype('uint8'))
        sv_result_image = Image.fromarray(white_sv_array.astype('uint8'))
        # 保存提取的图像  
        tmp = os.path.join(extracted_ss_folder,img_names[i])
        ss_result_image.save(tmp)
        tmp = os.path.join(extracted_sv_folder,img_names[i])
        sv_result_image.save(tmp)

if __name__ == "__main__":
    image_folder =r'e:\work\20250709_sv_michinen\20251021\svi\svi_pan03'
    extracted_ss_folder = image_folder.replace('svi_pan03','ade_20k\_04_ss_extracted')
    if not os.path.exists(extracted_ss_folder):
        os.makedirs(extracted_ss_folder)
    extracted_sv_folder = image_folder.replace('svi_pan03','ade_20k\_05_sv_extracted')
    if not os.path.exists(extracted_sv_folder):
        os.makedirs(extracted_sv_folder)
        
    roots = []
    img_names = []
    img_paths = []

    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg")

    for root, dirs, files in os.walk(image_folder):
        for file in files:
            if file.endswith(accepted_formats):
                roots.append(root)
                img_names.append(file)
                file_path = os.path.join(root, file)
                img_paths.append(file_path)

    color_list = []
    colors = scipy.io.loadmat(r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\github\Fi-Mao-Tech\citycolorImpression\data\color150.mat')['colors']

    # 在for循环列表中，将5、18、67 植物 替换为你想要的语义分割的颜色索引编号
    # 在for循环列表中，将2 建筑
    # for i in [5,18,67]:
    for i in [2]:
        color_list.append(colors[i-1])

    extracted_arch(img_paths,img_names,extracted_ss_folder,extracted_sv_folder)
    



    