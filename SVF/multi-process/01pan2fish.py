# -*- coding: utf-8 -*-

import cv2
import numpy as np
import math
from math import pi, atan
from PIL import Image
import os
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import functools

def create_fisheye_single(args):
    file_n, overwrite = args
    out_name = file_n.replace('ade_20k_rgb', '半球_fisheye')
    
    if not overwrite and os.path.exists(out_name):
        return
    
    try:
        # 使用Pillow打开图片
        pil_img = Image.open(file_n)
        width, height = pil_img.size
        upper_half = pil_img.crop((0, 0, width, height // 2))
        _img = np.array(upper_half)
        _img = cv2.cvtColor(_img, cv2.COLOR_RGB2BGR) 
        height, width = _img.shape[:2]
        
        cx = width / (2 * math.pi)
        cy = width / (2 * math.pi)
        img_hemi = np.zeros((int(cx + 1) * 2, int(cx + 1) * 2, 3), dtype=np.uint8)
        
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
        mask = cv2.circle(mask, (int(cx + 1), int(cx + 1)), int(cx + 1), (255, 255, 255), -1)
        result = cv2.bitwise_and(img_hemi, mask)
        
        folder_path = os.path.dirname(out_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB) 
        pil_image = Image.fromarray(result_rgb) 
        pil_image.save(out_name)
    except Exception as e:
        print(f"Error processing {file_n}: {str(e)}")
        return file_n

def process_images_multiprocess(img_paths, num_processes=None, overwrite=False):
    if num_processes is None:
        num_processes = cpu_count()-2
    
    print(f"Using {num_processes} processes")
    
    with Pool(num_processes) as pool:
        # 准备参数列表
        args = [(path, overwrite) for path in img_paths]
        
        # 使用imap_unordered和tqdm显示进度
        results = list(tqdm(pool.imap_unordered(create_fisheye_single, args), 
                           total=len(img_paths),
                           desc="Processing images"))
    
    # 检查是否有处理失败的图片
    failed = [r for r in results if r is not None]
    if failed:
        print(f"\nFailed to process {len(failed)} images:")
        for f in failed:
            print(f)

def main():
    image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    img_paths = []
    
    root_dir = r'E:\work\sv_huang_g\test - 副本\ade_20k_rgb'
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(image_types):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
    
    # 设置是否覆盖已存在的文件
    overwrite_existing = False
    
    # 设置进程数 (None为自动检测CPU核心数)
    num_processes = None
    
    process_images_multiprocess(img_paths, num_processes, overwrite_existing)

if __name__ == '__main__':
    main()