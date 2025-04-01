import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

def calculate_brightness_saturation(img):
    """计算图片的亮度和饱和度"""
    # 转换为HSV色彩空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 亮度是V通道的平均值
    brightness = np.mean(hsv[:,:,2]) / 255.0
    
    # 饱和度是S通道的平均值
    saturation = np.mean(hsv[:,:,1]) / 255.0
    
    return brightness, saturation

def process_images(root_dir, output_csv, start_index=0, end_index=None, batch_size=1000):
    """处理图片并保存结果"""
    # 收集所有图片路径
    image_paths = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_paths.append(os.path.join(dirpath, filename))
    
    # 如果输出文件已存在，加载已有数据
    existing_data = pd.DataFrame(columns=['path', 'brightness', 'saturation'])
    if os.path.exists(output_csv):
        existing_data = pd.read_csv(output_csv)
        processed_paths = set(existing_data['path'])
    else:
        processed_paths = set()
    
    results = []
    batch_count = 0
    start_index=0, end_index=None,
    # 使用tqdm显示进度条
    for i, img_path in enumerate(tqdm(image_paths, desc="Processing images")):
        # 跳过已处理的图片
        if img_path in processed_paths:
            continue

        # 应用索引范围控制
        if i < start_index:
            continue
        if end_index is not None and i >= end_index:
            break

        try:
            # 使用Pillow打开图片
            pil_img = Image.open(img_path)
            img = np.array(pil_img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Pillow使用RGB格式，OpenCV使用BGR格式

            # img = cv2.imread(img_path)
            if img is None:
                continue
                
            # 计算亮度和饱和度
            brightness, saturation = calculate_brightness_saturation(img)
            
            # 添加到结果
            results.append({
                'path': img_path,
                'brightness': brightness,
                'saturation': saturation
            })
            
            # 每batch_size条保存一次
            if len(results) >= batch_size:
                save_results(output_csv, results, existing_data)
                existing_data = pd.read_csv(output_csv)
                processed_paths = set(existing_data['path'])
                results = []
                batch_count += 1
                print(f"Saved batch {batch_count} to {output_csv}")
                
        except Exception as e:
            print(f"Error processing {img_path}: {str(e)}")
            continue
    
    # 保存剩余结果
    if results:
        save_results(output_csv, results, existing_data)
        print(f"Saved final batch to {output_csv}")

def save_results(output_csv, new_results, existing_data):
    """保存结果到CSV"""
    new_df = pd.DataFrame(new_results)
    
    if os.path.exists(output_csv):
        # 合并新数据和已有数据
        combined_df = pd.concat([existing_data, new_df], ignore_index=True)
        # 去重，保留最后出现的记录
        combined_df = combined_df.drop_duplicates(subset=['path'], keep='last')
    else:
        combined_df = new_df
    
    combined_df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    # 用户可配置参数
    root_directory = r"E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_山南"  # 替换为你的文件夹路径
    output_csv_file = r"E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_山南_brightness_saturation.csv"  # 输出CSV文件名
    start_idx = 0  # 起始索引
    end_idx = None  # 结束索引（None表示处理所有）
    
    # 处理图片
    process_images(root_directory, output_csv_file, start_idx, end_idx)
    
    print("Processing completed!")