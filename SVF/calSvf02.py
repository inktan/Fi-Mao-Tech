# _*_ coding: utf-8 _*_
import cv2
import os
import math
import sys
import numpy as np
import pandas as pd
from multiprocessing import Pool, cpu_count
from datetime import datetime

from tqdm import tqdm  # 进度条库

def process_image(inputimg):
    try:
        # Read and resize image
        fisheye_img = cv2.imdecode(np.fromfile(inputimg, dtype=np.uint8), cv2.IMREAD_COLOR)
        fisheye_img = cv2.resize(fisheye_img, (173, 173), interpolation=cv2.INTER_LINEAR)
        
        # Initialize variables
        svf = 0.00
        r = 82
        
        # Pre-compute sin values
        sin_values = np.sin(np.pi * (2 * np.arange(1, 28) - 1) / 54)
        
        for index in range(27):
            # Create mask for the current circle
            y, x = np.ogrid[:173, :173]
            mask = (x - 86)**2 + (y - 86)**2 <= r**2
            inner_mask = (x - 86)**2 + (y - 86)**2 <= (r-3)**2
            circle_mask = mask & ~inner_mask
            
            # Get circle points
            circle_pixels = fisheye_img[circle_mask]
            
            # Identify sky pixels (vectorized operation)
            sky_mask = (circle_pixels[:, 2] >= 0) & (circle_pixels[:, 2] <= 10) & \
                       (circle_pixels[:, 1] >= 220) & (circle_pixels[:, 1] <= 240) & \
                       (circle_pixels[:, 0] >= 220) & (circle_pixels[:, 0] <= 240)
            
            sky_ratio = np.mean(sky_mask)
            svf += sin_values[index] * sky_ratio
            
            r -= 3
        
        svf = (math.pi / 54) * svf
        return {
            'image_path': inputimg,
            'sky_view_factor': svf,
            # 'processing_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"处理图片 {inputimg} 时出错: {str(e)}")
        # return {
        #     'image_path': inputimg,
        #     'sky_view_factor': 0.0,
            # 'processing_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            # 'error': str(e)
        # }

def save_results_to_csv(results, output_file):
    """将结果保存到CSV文件"""
    df = pd.DataFrame(results)
    
    # 如果文件已存在，追加数据
    # if os.path.exists(output_file):
    #     existing_df = pd.read_csv(output_file)
    #     df = pd.concat([existing_df, df], ignore_index=True)
    
    # 保存到CSV
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"结果已保存到 {output_file}")

def get_image_paths(root_dir, image_types):
    img_paths = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(image_types):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
    return img_paths
def main():
    
    """主函数"""
    print("开始处理图片...")
    start_time = datetime.now()

    root_dir = r'E:\work\sv_huang_g\街景全景图\半球_fisheye'
    image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    output_csv = r'E:\work\sv_huang_g\街景全景图\sky_view_factor_results.csv'

    img_paths = get_image_paths(root_dir, image_types)
    # img_paths = img_paths[:200]

    print(f"共找到 {len(img_paths)} 张图片需要处理")
    # Use multiprocessing
    num_processes = min(cpu_count()-2, len(img_paths))


    # 使用tqdm创建进度条
    with Pool(processes=num_processes) as pool:
        # 使用imap_unordered获取更流畅的进度条
        results = list(tqdm(pool.imap(process_image, img_paths), 
                          total=len(img_paths), 
                          desc="处理进度", 
                          unit="图片",
                          ncols=100))  # 控制进度条宽度
    
    # 保存结果到CSV
    save_results_to_csv(results, output_csv)
    
    # 打印处理摘要
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"处理完成! 共处理 {len(results)} 张图片")
    print(f"总耗时: {duration:.2f} 秒")
    print(f"平均每张图片处理时间: {duration/len(results):.4f} 秒")

if __name__ == '__main__':
    main()