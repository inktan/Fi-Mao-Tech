# 为了用一个数值表达图片的和谐度（色相和饱和度标准差的综合结果），
# 我们可以计算色相（Hue）和饱和度（Saturation）标准差的加权平均值或直接取均值。
# 由于色相和饱和度的数值范围不同（色相通常0-360°或0-179，饱和度0-255），
# 我们可能需要先归一化，再计算综合和谐度。

# 最终方案
# 计算色相（Hue）和饱和度（Saturation）的标准差

# 归一化标准差（使色相和饱和度的标准差在相同尺度下比较）

# 综合和谐度 = 色相标准差 + 饱和度标准差（越小越和谐）

# 也可以取均值或加权平均，这里简单相加。
import os
from PIL import Image
import numpy as np
from multiprocessing import Pool
from functools import partial
from tqdm import tqdm  # 导入进度条库
import csv

def calculate_hue_std(image_path):
    """计算单张图片的色相（Hue）标准差"""
    try:
        img = Image.open(image_path).convert('HSV')
        hsv_array = np.array(img)
        hue = hsv_array[:, :, 0].flatten()  # 提取色相通道（0-179）
        hue_std = np.std(hue) / 179.0       # 归一化到 [0, 1]
        return hue_std
    except Exception as e:
        print(f"\nError processing {image_path}: {e}")
        return None

def process_images(folder_path, num_processes=None):
    """多进程批量处理文件夹中的图片（带进度条）"""
    # 获取所有图片文件
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    image_files = [
        os.path.join(folder_path, f) 
        for f in os.listdir(folder_path) 
        if f.lower().endswith(image_extensions)
    ]
    
    if not image_files:
        print("No images found in the folder!")
        return {}
    
    # 使用多进程计算色相标准差（带进度条）
    with Pool(processes=num_processes) as pool:
        # 使用tqdm创建进度条
        results = list(tqdm(
            pool.imap(calculate_hue_std, image_files),
            total=len(image_files),
            desc="Processing Images",
            unit="image"
        ))
    
    # 返回 {文件名: 色相标准差}
    return {
        os.path.basename(image_file): std 
        for image_file, std in zip(image_files, results) 
        if std is not None
    }

def save_results_to_csv(results, output_file="harmony_results.csv"):
    """将结果保存为CSV文件"""
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "Hue STD (Normalized)"])
        for filename, std in sorted(results.items(), key=lambda x: x[1]):
            writer.writerow([filename, f"{std:.4f}"])
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    folder_path = "E:\work\sv_xiufenganning\地理数据\svi_degrees"  # 替换为你的文件夹路径
    num_processes = 4  # 进程数（默认使用CPU核心数，None=自动选择）
    
    print(f"Starting processing {folder_path} with {num_processes} processes...")
    harmony_results = process_images(folder_path, num_processes)
    
    # 打印结果摘要
    print("\nTop 5 most harmonious images:")
    for filename, std in sorted(harmony_results.items(), key=lambda x: x[1])[:5]:
        print(f"  {filename}: {std:.4f}")
    
    save_results_to_csv(harmony_results)