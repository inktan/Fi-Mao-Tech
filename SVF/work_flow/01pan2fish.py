# -*- coding: utf-8 -*-

import cv2
import numpy as np
import math
from math import pi,atan

import numpy as np
from PIL import Image
import os
from tqdm import tqdm

def create_fisheye(file_n):
    out_name = file_n.replace(r'results', r'sv_pan_fisheye')
    if os.path.exists(out_name):
        return
    # 使用Pillow打开图片
    pil_img = Image.open(file_n)
    width, height = pil_img.size
    upper_half = pil_img.crop((0, 0, width, height // 2))
    _img = np.array(upper_half)
    _img = cv2.cvtColor(_img, cv2.COLOR_RGB2BGR) 
    height,width = _img.shape[:2]
    cx = width/(2*math.pi)
    cy = width/(2*math.pi)
    img_hemi = np.zeros((int(cx+1)*2,int(cx+1)*2,3),dtype=np.uint8)
    for col in range(img_hemi.shape[0]):
        for row in range(img_hemi.shape[1]):
            if row < cy: 
                if col < cx:
                    theta = np.pi - atan((row - cy) / (col - cx))
                else: 
                    theta = np.abs(atan((row - cy) / (col - cx)))
            else:
                if col < cx: 
                    theta = np.pi + np.abs(atan((row - cy) / (col - cx)))
                else: 
                    theta = 2 * np.pi - atan((row - cy) / (col - cx))
            r = np.sqrt((col - cx) ** 2 + (row - cy) ** 2)
            x = (theta * width) / (2 * pi)
            y = (r * height) / cy
            img_hemi[row][col] = cv2.getRectSubPix(_img, (1, 1), (x, y))
    mask = np.zeros_like(img_hemi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    mask = cv2.circle(mask, (int(cx + 1), int(cx + 1)), int(cx + 1), (255, 255, 255), -1)
    result = cv2.bitwise_and(img_hemi, mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    out_name = file_n.replace('results', '半球_fisheye')
    folder_path = os.path.dirname(out_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB) 
    pil_image = Image.fromarray(result_rgb) 
    pil_image.save(out_name)

image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
img_paths = []
roots = []
img_names = []

for root, dirs, files in os.walk(r'E:\work\sv_huang_g\test\results'):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
            roots.append(root)

for i,image_path in enumerate(tqdm(img_paths)): 
    # if i<=10000:
    #     continue
    # if i>8000000:
    #     continue
    create_fisheye(image_path)
    
    
    
    
    
    
    