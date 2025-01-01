import os

from PIL import Image  
from collections import defaultdict  
from tqdm import tqdm
import math
import csv

# -*- coding: utf-8 -*-
# 一种街道两侧建筑色彩协调度计算方法

def split_and_count_pixels(image_path):  
    # 加载图像  
    img = Image.open(image_path)  
    width, height = img.size  
  
    # 确保图像宽度是偶数，以便可以平均分割  
    # if width % 2 != 0:  
    #     raise ValueError("Image width should be an even number for even splitting.")  
    
    half_width = width // 2  
    # 分割图像为左右两半  
    left_img = img.crop((0, 0, half_width, height))  
    right_img = img.crop((half_width, 0, width, height))  
    # 初始化字典来存储左右两半图像的像素统计信息  
    left_pixel_counts = defaultdict(int)  
    right_pixel_counts = defaultdict(int)  
    
    # 统计左半图像的像素值  
    for x in range(half_width):  
        for y in range(height):  
            r, g, b = left_img.getpixel((x, y))
            if (r, g, b) !=(255,255,255):
                ki = b*8*8 + g*8 + r
                left_pixel_counts[ki] += 1  

    # 统计右半图像的像素值  
    for x in range(half_width):  
        for y in range(height):  
            r, g, b = right_img.getpixel((x, y))  
            if (r, g, b) !=(255,255,255):
                ki = b*8*8 + g*8 + r
                right_pixel_counts[ki] += 1  
    
    ch_01 = sum([left_pixel_counts[i]*right_pixel_counts[i] for i in range(1,513)])
    ch_l = sum([left_pixel_counts[i]*left_pixel_counts[i] for i in range(1,513)])
    ch_r = sum([right_pixel_counts[i]*right_pixel_counts[i] for i in range(1,513)])

    if ch_l == 0 or ch_r == 0:
        return 0
    else:
        ch = ch_01/( math.sqrt(ch_l) * math.sqrt(ch_r))
        return ch

def main(image_paths,img_names):
    # with open(r'F:\sv\街景\color_coordination_sv.csv','w' ,newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(['image_name','CH'])

    for i,img_path in enumerate(tqdm(image_paths)):
        if i<29000:
            continue
        image_path = os.path.join(img_path, img_names[i])
        try:
            ch = split_and_count_pixels(image_path) 
            with open(r'F:\sv\街景\color_coordination_sv.csv','a' ,newline='') as f:
                writer = csv.writer(f)
                writer.writerow([img_names[i],ch])

        except Exception as e:
            continue
    return

if __name__ == "__main__":

    img_paths = []
    img_names = []
    for root, dirs, files in os.walk(r'F:\sv\街景\sv_arch'):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png"):
                img_paths.append(root)
                img_names.append(file)

    main(img_paths,img_names)

