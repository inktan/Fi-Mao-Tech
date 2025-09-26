from PIL import Image
import os
import numpy as np
from tqdm import tqdm
import time
from multiprocessing import Pool, cpu_count, Manager
import argparse
from functools import partial

# 移除图像像素限制
Image.MAX_IMAGE_PIXELS = None

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} 耗时: {elapsed_time:.2f} 秒")
        return result
    return wrapper

def process_single_image(args):
    """处理单个图像的函数，用于多进程"""
    file_path, black_threshold = args
    try:
        image = Image.open(file_path)
        img_array = np.array(image)
        
        # 判断黑色像素
        if len(img_array.shape) == 3:  # RGB图像
            black_pixels = (img_array == [0, 0, 0]).all(axis=2)
        else:  # 灰度图像
            black_pixels = (img_array == 0)

        num_black_pixels = np.sum(black_pixels)
        total_pixels = img_array.size // 3 if len(img_array.shape) == 3 else img_array.size

        black_pixel_ratio = num_black_pixels / total_pixels
        
        # 判断黑色像素比例是否大于阈值
        if black_pixel_ratio > black_threshold:
            try:
                os.remove(file_path)
                return file_path, True, black_pixel_ratio
            except Exception as e:
                return file_path, False, black_pixel_ratio
        else:
            return file_path, False, black_pixel_ratio
            
    except Exception as e:
        return file_path, False, 0.0

def remove_black_images_parallel(img_paths, black_threshold=0.30, num_processes=None):
    """并行移除黑色图像"""
    if num_processes is None:
        num_processes = cpu_count()
    
    print(f"使用 {num_processes} 个进程处理 {len(img_paths)} 张图片")
    
    # 准备参数
    tasks = [(path, black_threshold) for path in img_paths]
    
    # 使用多进程处理
    removed_count = 0
    processed_count = 0
    
    with Pool(processes=num_processes) as pool:
        # 使用imap_unordered提高效率
        results = list(tqdm(pool.imap_unordered(process_single_image, tasks), 
                          total=len(tasks), 
                          desc="处理图片"))
    
    # 统计结果
    removed_files = []
    for file_path, removed, ratio in results:
        processed_count += 1
        if removed:
            removed_count += 1
            removed_files.append(file_path)
    
    print(f"处理完成: 总共 {processed_count} 张图片, 移除 {removed_count} 张黑色图片")
    return removed_files

def get_image_paths(folder_paths, accepted_formats=(".png", ".jpg", ".JPG", ".jpeg", ".webp")):
    """获取所有图片路径"""
    img_paths = []
    for folder_path in folder_paths:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
    return img_paths

@timer_decorator
def main():
    # 配置参数
    folder_paths = [
        r'E:\stree_view',
    ]
    
    black_threshold = 0.30  # 黑色像素阈值
    num_processes = cpu_count()  # 使用所有CPU核心
    
    # 获取所有图片路径
    print("正在扫描图片文件...")
    img_paths = get_image_paths(folder_paths)
    print(f"找到 {len(img_paths)} 张图片")
    
    if not img_paths:
        print("没有找到图片文件")
        return
    
    # 并行处理图片
    removed_files = remove_black_images_parallel(img_paths, black_threshold, num_processes)
    
    # 输出被移除的文件列表
    if removed_files:
        print("\n被移除的黑色图片:")
        for file_path in removed_files[:10]:  # 只显示前10个
            print(f"  {file_path}")
        if len(removed_files) > 10:
            print(f"  ... 还有 {len(removed_files) - 10} 个文件")

def process_in_batches(img_paths, batch_size=1000, black_threshold=0.30, num_processes=None):
    """分批处理图片，避免内存不足"""
    if num_processes is None:
        num_processes = cpu_count()
    
    total_removed = 0
    total_processed = 0
    
    for i in range(0, len(img_paths), batch_size):
        batch = img_paths[i:i + batch_size]
        print(f"处理批次 {i//batch_size + 1}/{(len(img_paths)-1)//batch_size + 1}, 图片数: {len(batch)}")
        
        removed_files = remove_black_images_parallel(batch, black_threshold, num_processes)
        total_removed += len(removed_files)
        total_processed += len(batch)
        
        # 显示进度
        current_time = time.strftime("%H:%M:%S")
        print(f"[{current_time}] 已处理: {total_processed}/{len(img_paths)} "
              f"({total_processed/len(img_paths)*100:.1f}%), "
              f"移除: {total_removed}")
    
    return total_removed

if __name__ == '__main__':
    print('开始处理图片...')
    
    # 添加命令行参数支持
    parser = argparse.ArgumentParser(description='移除黑色图片')
    parser.add_argument('--threshold', type=float, default=0.30, help='黑色像素阈值 (默认: 0.30)')
    parser.add_argument('--processes', type=int, default=None, help='进程数 (默认: 使用所有CPU核心)')
    parser.add_argument('--batch-size', type=int, default=1000, help='每批处理图片数 (默认: 1000)')
    
    args = parser.parse_args()
    
    # 配置参数
    folder_paths = [r'E:\stree_view']
    black_threshold = args.threshold
    num_processes = args.processes
    batch_size = args.batch_size
    
    print(f"配置: 阈值={black_threshold}, 进程数={num_processes or '自动'}, 批次大小={batch_size}")
    
    # 获取所有图片路径
    print("正在扫描图片文件...")
    img_paths = get_image_paths(folder_paths)
    print(f"找到 {len(img_paths)} 张图片")
    
    if not img_paths:
        print("没有找到图片文件")
        exit()
    
    # 分批处理
    start_time = time.time()
    total_removed = process_in_batches(img_paths, batch_size, black_threshold, num_processes)
    
    total_time = time.time() - start_time
    print(f"\n处理完成! 总共处理 {len(img_paths)} 张图片, 移除 {total_removed} 张黑色图片")
    print(f"总耗时: {total_time:.2f} 秒")
    print(f"平均速度: {len(img_paths)/total_time:.2f} 图片/秒")