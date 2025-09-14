import os
import cv2
import pandas as pd
from pathlib import Path
import argparse
import numpy as np
from tqdm import tqdm
import time
from datetime import datetime

def is_image_black_dominant(image_path, threshold=0.5):
    """
    检查图片中黑色像素是否超过指定比例
    
    参数:
    image_path: 图片路径
    threshold: 黑色像素比例阈值，默认0.5(50%)
    
    返回:
    bool: 如果黑色像素比例超过阈值返回1，否则返回0
    """
    try:
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            print(f"无法读取图片: {image_path}")
            return 0
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 计算黑色像素数量 (像素值小于等于30认为是黑色)
        black_pixels = np.sum(gray <= 30)
        total_pixels = gray.size
        
        # 计算黑色像素比例
        black_ratio = black_pixels / total_pixels
        
        return 1 if black_ratio > threshold else 0
        
    except Exception as e:
        print(f"处理图片时出错 {image_path}: {e}")
        return 0

def process_images_to_csv(folder_path, output_csv, batch_size=1000, progress_interval=10000):
    """
    处理文件夹中的所有图片并保存到CSV文件
    
    参数:
    folder_path: 输入文件夹路径
    output_csv: 输出CSV文件路径
    batch_size: 每处理多少张图片保存一次
    progress_interval: 进度报告间隔（每处理多少张图片输出一次时间）
    """
    # 支持的图片格式
    image_extensions = {'.jpg'}
    
    # 收集所有图片路径
    image_paths = []
    folder_path = Path(folder_path)
    
    print("正在搜索图片文件...")
    for ext in image_extensions:
        image_paths.extend(folder_path.rglob(f"*{ext}"))
        image_paths.extend(folder_path.rglob(f"*{ext.upper()}"))
    
    total_images = len(image_paths)
    print(f"找到 {total_images} 张图片")
    
    if total_images == 0:
        print("未找到任何图片文件，程序退出")
        return
    
    # 准备数据存储
    data = []
    results_df = pd.DataFrame(columns=['image_name', 'is_black'])
    
    # 如果文件已存在，读取已有数据
    processed_images = set()
    if os.path.exists(output_csv):
        try:
            existing_df = pd.read_csv(output_csv)
            processed_images = set(existing_df['image_name'].tolist())
            results_df = existing_df
            print(f"发现已有CSV文件，包含 {len(processed_images)} 条记录")
            print("将跳过已处理的图片...")
        except Exception as e:
            print(f"读取现有CSV文件时出错: {e}")
            processed_images = set()
    
    # 过滤掉已处理的图片
    unprocessed_paths = [path for path in image_paths if str(path) not in processed_images]
    images_to_process = len(unprocessed_paths)
    
    if images_to_process == 0:
        print("所有图片都已处理完成！")
        return
    
    print(f"需要处理 {images_to_process} 张新图片")
    
    # 创建进度条
    progress_bar = tqdm(
        total=images_to_process,
        desc="处理图片进度",
        unit="张",
        ncols=100,
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
    )
    
    start_time = time.time()
    last_progress_time = start_time
    
    # 处理图片
    for i, img_path in enumerate(unprocessed_paths):
        img_path_str = str(img_path)
        
        # 检查是否为黑色主导
        is_black = is_image_black_dominant(img_path_str)
        
        # 添加到数据列表
        data.append({
            'image_name': img_path_str,
            'is_black': is_black
        })
        
        # 更新进度条
        progress_bar.update(1)
        progress_bar.set_postfix({
            '当前': f"{i+1}/{images_to_process}",
            '黑色图片': f"{sum(item['is_black'] for item in data)}"
        })
        
        # 每处理progress_interval张图片输出一次当前时间
        if (i + 1) % progress_interval == 0:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elapsed_time = time.time() - start_time
            processed_per_second = (i + 1) / elapsed_time if elapsed_time > 0 else 0
            
            print(f"\n[{current_time}] 已处理 {i+1} 张图片, "
                  f"速度: {processed_per_second:.2f} 张/秒, "
                  f"已运行: {elapsed_time:.2f} 秒")
        
        # 每处理batch_size张图片或处理完所有图片时保存一次
        if len(data) >= batch_size or i == images_to_process - 1:
            if data:  # 确保有数据才保存
                # 创建新的DataFrame并合并
                new_df = pd.DataFrame(data)
                results_df = pd.concat([results_df, new_df], ignore_index=True)
                
                # 保存到CSV
                results_df.to_csv(output_csv, index=False)
                
                # 清空临时数据
                data = []
                
                # 更新进度条描述
                progress_bar.set_description(f"处理图片进度 (已保存 {len(results_df)} 条记录)")
    
    # 关闭进度条
    progress_bar.close()
    
    # 输出最终统计信息
    end_time = time.time()
    total_time = end_time - start_time
    black_count = results_df['is_black'].sum()
    black_ratio = (black_count / len(results_df)) * 100 if len(results_df) > 0 else 0
    
    print(f"\n处理完成！")
    print(f"总处理时间: {total_time:.2f} 秒")
    print(f"总图片数量: {len(results_df)} 张")
    print(f"黑色图片数量: {black_count} 张 ({black_ratio:.2f}%)")
    print(f"平均处理速度: {len(results_df)/total_time:.2f} 张/秒")
    print(f"结果已保存到: {output_csv}")

def main():
    parser = argparse.ArgumentParser(description='处理图片并检测黑色像素比例')
    parser.add_argument('--input', '-i', required=True, help='输入文件夹路径')
    parser.add_argument('--output', '-o', default='image_analysis.csv', help='输出CSV文件路径')
    parser.add_argument('--batch', '-b', type=int, default=1000, help='批量处理大小')
    parser.add_argument('--progress-interval', '-p', type=int, default=10000, 
                       help='进度报告间隔（每处理多少张图片输出一次时间）')
    
    args = parser.parse_args()
    
    # 检查输入文件夹是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件夹 {args.input} 不存在")
        return
    
    process_images_to_csv(args.input, args.output, args.batch, args.progress_interval)

if __name__ == "__main__":
    # 安装tqdm: pip install tqdm
    
    # 如果没有通过命令行运行，可以直接设置参数
    if len(os.sys.argv) == 1:
        # 在这里设置默认参数
        input_folder = r"e:\stree_view"  # 修改为你的图片文件夹路径
        output_file = r"e:\image_analysis.csv"
        batch_size = 3000
        progress_interval = 3000
        
        if os.path.exists(input_folder):
            process_images_to_csv(input_folder, output_file, batch_size, progress_interval)
        else:
            print("请通过命令行参数指定输入文件夹，或修改脚本中的默认路径")
            print("用法: python script.py --input <文件夹路径> [--output <输出文件>] [--batch <批量大小>] [--progress-interval <进度间隔>]")
    else:
        main()