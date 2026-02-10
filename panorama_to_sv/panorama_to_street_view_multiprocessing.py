# -*- coding: utf-8 -*-

import os
import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import Equirec2Perspec as E2P

# 将单张图片的处理逻辑封装，供进程池调用
def process_single_image(image_path, fov, degree_count, phi, height, width):
    image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    if not image_path.lower().endswith(image_types):
        return
    
    try:
        # 加载全景图
        equ = E2P.Equirectangular(image_path)
        
        degree_avg = 360 / degree_count
        degrees = [i * degree_avg for i in range(degree_count)]
        
        image_type = image_path.split('.')[-1]
        
        for deg in degrees:
            # 路径替换逻辑
            img_degree_save = image_path.replace('svi_google', 'svi_google_degree').replace('.' + image_type, f'_{int(deg)}.{image_type}')
            
            # 如果文件已存在，跳过
            if os.path.exists(img_degree_save):
                continue

            # 转换透视图
            img = equ.GetPerspective(fov, deg, phi, height, width)
            
            # 颜色空间转换与保存
            persp_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(persp_rgb)

            # 确保目录存在（使用 exist_ok=True 防止多进程冲突）
            folder_path = os.path.dirname(img_degree_save)
            os.makedirs(folder_path, exist_ok=True)

            pil_image.save(img_degree_save)
            
    except Exception as e:
        return f"Error processing {image_path}: {e}"

def panorama_to_street_view_parallel(input_dir, fov, degree_count, phi, height, width):
    # 1. 预先收集所有待处理文件路径
    img_paths = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith((".jpg", ".png", ".jpeg")):
                img_paths.append(os.path.join(root, file))

    # 2. 获取计算机 CPU 核心数
    max_workers = os.cpu_count()
    print(f"检测到 {max_workers} 个核心，启动多进程处理...")

    # 3. 使用进程池进行并行处理
    # chunksize 指定每个进程一次分担的任务数，增加它可以减少进程切换开销
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 准备固定参数
        from functools import partial
        worker_func = partial(process_single_image, fov=fov, degree_count=degree_count, 
                              phi=phi, height=height, width=width)
        
        # 使用 tqdm 显示进度条
        list(tqdm(executor.map(worker_func, img_paths), total=len(img_paths), desc="处理进度"))

# ------------ 主函数 -------------------
if __name__ == "__main__":
    # 注意：在 Windows 下，多进程代码必须放在 if __name__ == "__main__": 之下
    input_path = r'F:\osm\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\澳门特别行政区\svi_google'
    
    config = {
        "fov": 90,
        "phi": 0,
        "degree_count": 4,
        "width": 2048,
        "height": 1536
    }

    panorama_to_street_view_parallel(
        input_path, 
        config["fov"], 
        config["degree_count"], 
        config["phi"], 
        config["height"], 
        config["width"]
    )