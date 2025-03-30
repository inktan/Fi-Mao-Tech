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
    result = cv2.imread(file_n)
    if result is None:
        raise FileNotFoundError("无法加载图像，请检查路径")
    h, w = result.shape[:2] 
    cx, cy = w // 2, h // 2
    angle = 30 
    scale = 1.0 
    M = cv2.getRotationMatrix2D((cx, cy), angle, scale)
    rotated = cv2.warpAffine(result, M, (w, h))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    output_file = file_n.replace('fisheye','fisheye_R')
    folder_path = os.path.dirname(output_file)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    cv2.imwrite(output_file, rotated)
    # print(f"图像已保存至: {output_file}")

image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
img_paths = []
roots = []
img_names = []
for root, dirs, files in os.walk(r'E:\work\sv_j_ran\20241227\pan2fish\fisheye'):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
            roots.append(root)
for i,image_path in enumerate(tqdm(img_paths)): 
    rotate_fisheye(image_path)
    