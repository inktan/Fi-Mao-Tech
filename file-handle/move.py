import os
from PIL import Image
import shutil
from pathlib import Path
import numpy as np
from PIL import Image

def is_bottom_folder(folder_path):
    """检查是否为最底层文件夹（没有子文件夹或子文件夹不含.jpg文件）"""
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            # 检查子文件夹是否包含.jpg文件
            for root, _, files in os.walk(item_path):
                if any(f.lower().endswith('.jpg') for f in files):
                    return False
    return True

def find_jpg_folders(root_dir):
    """查找包含.jpg文件的最底层文件夹"""
    jpg_folders = []
    
    for foldername, subfolders, filenames in os.walk(root_dir):
        if not is_bottom_folder(foldername):
            continue
            
        has_jpg = any(filename.lower().endswith('.jpg') for filename in filenames)
        if has_jpg:
            jpg_folders.append(foldername)
    
    return jpg_folders

def has_high_black_ratio(image_path, threshold=0.5):
    """
    判断图片中指定颜色的像素占比是否超过给定阈值
    
    参数:
        image_path: 图片路径
        target_color: 目标颜色，格式为(R, G, B)
        threshold: 占比阈值(0-1之间)
        
    返回:
        bool: 如果目标颜色像素占比超过阈值返回True，否则返回False
    """
    # 打开图片并转换为RGB模式
    img = Image.open(image_path).convert('RGB')
    
    # 将图片转换为NumPy数组
    img_array = np.array(img)
    
    # 计算目标颜色的像素数
    
    target_color = [237, 234, 227]

    # 使用 np.all() 检查每个像素是否完全匹配目标颜色
    matches = np.all(img_array == target_color, axis=-1)

    # 统计匹配的像素数量
    target_count = np.sum(matches)

    # 计算总像素数
    total_pixels = img_array.shape[0] * img_array.shape[1]
    
    # 计算占比
    proportion = target_count / total_pixels
    
    # 判断是否超过阈值
    return proportion > threshold


def check_and_delete_folders(jpg_folders):
    """检查文件夹中的图片并删除符合条件的文件夹"""
    deleted_folders = 0
    
    for folder in jpg_folders:
        delete_folder = False
        for filename in os.listdir(folder):
            if filename.lower().endswith('.jpg'):
                image_path = os.path.join(folder, filename)
                if has_high_black_ratio(image_path):
                    print(f"发现黑色占比高的图片: {image_path}")
                    delete_folder = True
                    break
        
        if delete_folder:
            try:
                shutil.rmtree(folder)
                print(f"已删除文件夹: {folder}")
                deleted_folders += 1
            except Exception as e:
                print(f"删除文件夹 {folder} 失败: {e}")
    
    return deleted_folders

if __name__ == "__main__":
    root_directory = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街景建筑分类_gs'
    
    jpg_folders = find_jpg_folders(root_directory)
    print(f"找到 {len(jpg_folders)} 个包含.jpg文件的最底层文件夹")
    
    if not jpg_folders:
        print("没有找到符合条件的文件夹")
        exit(0)
    
    print("开始检查图片黑色像素占比...")
    deleted_count = check_and_delete_folders(jpg_folders)
    print(f"处理完成! 共删除了 {deleted_count} 个文件夹")