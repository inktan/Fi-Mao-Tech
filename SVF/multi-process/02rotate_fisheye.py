# -*- coding: utf-8 -*-
import cv2
import numpy as np
import math
from math import pi,atan

import numpy as np
from PIL import Image
import os
from tqdm import tqdm

def rotate_fisheye(file_n):
    output_file = file_n.replace('fisheye','fisheye_R')
    if os.path.exists(output_file):
        return
    
    result = cv2.imread(file_n)
    if result is None:
        raise FileNotFoundError("无法加载图像，请检查路径")
    h, w = result.shape[:2] 
    cx, cy = w // 2, h // 2
    
    # 使用 _ 分割字符串
    parts = file_n.split('_')
    try:
        # 获取倒数第三个元素（索引为 -3），并转为浮点数
        angle = float(parts[-3])
        # print(result)
    except IndexError:
        print("分割后的元素不足三个！")
        return
    except ValueError:
        print("倒数第三个元素不是有效的浮点数！")
        return

    scale = 1.0 
    M = cv2.getRotationMatrix2D((cx, cy), angle, scale)
    rotated = cv2.warpAffine(result, M, (w, h))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    folder_path = os.path.dirname(output_file)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    cv2.imwrite(output_file, rotated)
    # print(f"图像已保存至: {output_file}")

image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
img_paths = []
roots = []
img_names = []
for root, dirs, files in os.walk(r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan_rgb_fisheye'):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
            roots.append(root)
for i,image_path in enumerate(tqdm(img_paths)): 
    if i<=-1:
        continue
    if i>10000:
        continue
    rotate_fisheye(image_path)
    