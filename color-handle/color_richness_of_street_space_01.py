
# -*- coding: utf-8 -*-
# 空间色彩丰富度

import pandas as pd
import os
import csv
import math

import numpy as np
from tqdm import tqdm

from PIL import Image
import numpy as np
import os
import cv2

# 定义计算CRI的函数
def calculate_cri_01(image_path):

    image = Image.open(image_path)
    # 将图片转换为NumPy数组  
    pixels = np.array(image) 
     # 获取所有唯一颜色  
    unique_colors, counts = np.unique(pixels.reshape(-1, pixels.shape[2]), axis=0, return_counts=True)  
    width, height = image.size
    pixel_count = width * height
    cri = 1 - sum((count / pixel_count) ** 2 for count in counts)

    return cri

def image_colorfulness(image_path): 
    image = Image.open(image_path)
    # 将图片转换为NumPy数组  
    image_array = np.array(image).astype("float")

    # 分别获取R、G、B通道的值
    R = image_array[:, :, 0]
    G = image_array[:, :, 1]
    B = image_array[:, :, 2]

    #rg = R - G
    rg = np.absolute(R - G) 

    #yb = 0.5 * (R + G) - B
    yb = np.absolute(0.5 * (R + G) - B) 

    #计算rg和yb的平均值和标准差
    (rbMean, rbStd) = (np.mean(rg), np.std(rg)) 
    (ybMean, ybStd) = (np.mean(yb), np.std(yb)) 

    #计算rgyb的标准差和平均值
    stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
    meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2)) 

    # 返回颜色丰富度C 
    return stdRoot/100 + (0.3 * meanRoot)/100

def main(folder_path,Level_Diversity_csv):
    with open('%s'%Level_Diversity_csv ,'w' ,newline='') as f: 
        writer = csv.writer(f)
        writer.writerow(['image_name', 'cri'])

    # 读取Excel文件
    df = pd.read_excel('e:\work\sv_renleihuoshifen\研究-指标.xlsx', engine='openpyxl')

    # 打印id列的每一行数据
    for index, row in df.iterrows():
        print(row['name'])
        # print(f"ID: {row['id']}, Data: {row}")

    # 获取文件夹中所有图片文件的路径
    # for index, image_name in  enumerate(tqdm([file for file in os.listdir(folder_path) if file.endswith(('png', 'jpg', 'jpeg'))])):
        # if index >= 1305:
        #     continue
        # 计算并打印每张图片的CRI
        path=os.path.join(folder_path, row['name']) 
        cri = image_colorfulness(path)
        
        rate_list = [row['name'],cri]

        with open('%s' % Level_Diversity_csv ,'a' ,newline='') as f:
            writer = csv.writer(f)
            writer.writerow(rate_list)

if __name__ == "__main__":
    '''
    空间色彩丰富度
    '''
    # folder_path = os.path.join(r"F:\BaiduNetdiskDownload\sv_renleiluoshifen\sv_澳门_degree_960_720\sv_degree_960_720")
    folder_path = os.path.join(r"E:\work\sv_renleihuoshifen\sv_degree_960_720")
    Level_Diversity_csv = os.path.join(r"E:\work\sv_renleihuoshifen\色彩丰富度-cri.csv")

    main(folder_path,Level_Diversity_csv)
    

