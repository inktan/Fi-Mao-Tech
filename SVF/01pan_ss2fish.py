# -*- coding: utf-8 -*-

import cv2
import numpy as np
import math
from math import pi,atan

import numpy as np
from PIL import Image
import os
from tqdm import tqdm

#创建鱼眼
# 鱼眼的半径r=width/2PI。街景分辨率为1024*256，则鱼眼的半径为1024/2PI=163
def create_fisheye(file_n):
    out_name = file_n.replace('sv_pan_rgb', 'sv_pan_rgb_fisheye')
    if os.path.exists(out_name):
        return

    # 使用Pillow打开图片
    pil_img = Image.open(file_n)
      # 获取图像的宽度和高度
    width, height = pil_img.size
    # 裁剪出图片的上半部分 为了得到半球
    upper_half = pil_img.crop((0, 0, width, height // 2))

    # 对于语义色块的处理，只保留天空
    upper_half_array = np.array(upper_half)
    color_to_keep = [6, 230, 230]
    mask = np.all(upper_half_array == color_to_keep, axis=-1)
    filtered_image = np.zeros_like(upper_half_array)
    filtered_image[mask] = upper_half_array[mask]
    upper_half = Image.fromarray(filtered_image)

    # 将裁剪后的图像转换为OpenCV格式
    _img = np.array(upper_half)
    _img = cv2.cvtColor(_img, cv2.COLOR_RGB2BGR)  # Pillow使用RGB格式，OpenCV使用BGR格式
    height,width = _img.shape[:2]
    cx = width/(2*math.pi)
    cy = width/(2*math.pi)
    img_hemi = np.zeros((int(cx+1)*2,int(cx+1)*2,3),dtype=np.uint8)
    #理解四个象限
    for col in range(img_hemi.shape[0]):  # col是x方向
        for row in range(img_hemi.shape[1]):  # row是y方向
            if row < cy:  # 界定第一、二象限
                if col < cx:  # 第二象限
                    theta = np.pi - atan((row - cy) / (col - cx))
                else:  # 第一象限
                    theta = np.abs(atan((row - cy) / (col - cx)))
            else:
                if col < cx:  # 第三象限
                    theta = np.pi + np.abs(atan((row - cy) / (col - cx)))
                else:  # 第四象限
                    theta = 2 * np.pi - atan((row - cy) / (col - cx))

            r = np.sqrt((col - cx) ** 2 + (row - cy) ** 2)

            x = (theta * width) / (2 * pi)
            y = (r * height) / cy

            img_hemi[row][col] = cv2.getRectSubPix(_img, (1, 1), (x, y))

    # 外围设置为黑色
    mask = np.zeros_like(img_hemi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    mask = cv2.circle(mask, (int(cx + 1), int(cx + 1)), int(cx + 1), (255, 255, 255), -1)
    result = cv2.bitwise_and(img_hemi, mask)  # 使用“与”操作函数cv2.bitwise_and()对图像掩膜（遮挡）
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # 保存图像
    folder_path = os.path.dirname(out_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    # print(out_name)
    # print(result.shape)
    # cv2.imwrite(out_name, result)
    # 在保存图像之前，将 OpenCV 图像转换为 Pillow 图像
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)  # 将 BGR 转换为 RGB
    pil_image = Image.fromarray(result_rgb)  # 将 NumPy 数组转换为 Pillow 图像

    # 保存图像
    pil_image.save(out_name)

# 定义图片文件类型  
image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
# 遍历输入文件夹中的所有图片文件，并进行处理
img_paths = []
roots = []
img_names = []

for root, dirs, files in os.walk(r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan_rgb'):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
            roots.append(root)

for i,image_path in enumerate(tqdm(img_paths)): 
    
    create_fisheye(image_path)
    