import shutil
import os
import time
from pathlib import Path

def batch_copy_images():
    base_source = r'e:\GoogleDrive\我的云端硬盘\work_fimo\svi_taiwan'
    base_destination = r'e:\svi_panorama'
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    # 生成所有文件夹名称
    folders = []
    for i in range(410000, 2340001, 10000):
        folders.append(f"sv_pano_{i}_{i + 10000}")
    
    total_folders = len(folders)
    print(f"发现 {total_folders} 个需要处理的文件夹")
    
    # 确保目标基础目录存在
    os.makedirs(base_destination, exist_ok=True)
    
    success_count = 0
    skip_count = 0
    error_count = 0
    total_images = 0
    copied_images = 0
    
    start_time = time.time()
    
    for index, folder in enumerate(folders, 1):
        source_path = os.path.join(base_source, folder)
        dest_path = os.path.join(base_destination, folder)
        
        print(f"[{index}/{total_folders}] 处理文件夹: {folder}")
        
        # 检查源路径是否存在
        if not os.path.exists(source_path):
            print(f"  跳过 - 源文件夹不存在")
            skip_count += 1
            continue
        
        # 创建目标文件夹
        os.makedirs(dest_path, exist_ok=True)
        
        # 遍历源文件夹中的所有文件
        try:
            files = os.listdir(source_path)
            image_files = [f for f in files if os.path.splitext(f)[1].lower() in image_extensions]
            
            if not image_files:
                print(f"  文件夹中没有图片文件")
                continue
            
            print(f"  发现 {len(image_files)} 张图片")
            total_images += len(image_files)
            
            # 逐张复制图片
            for img_index, image_file in enumerate(image_files, 1):
                src_file_path = os.path.join(source_path, image_file)
                dst_file_path = os.path.join(dest_path, image_file)
                
                # 检查目标文件是否已存在
                if os.path.exists(dst_file_path):
                    # print(f"    跳过图片 {img_index}/{len(image_files)}: {image_file} (已存在)")
                    continue
                
                try:
                    shutil.copy2(src_file_path, dst_file_path)
                    copied_images += 1
                    # print(f"    ✓ 复制图片 {img_index}/{len(image_files)}: {image_file}")
                    
                except Exception as e:
                    print(f"    ✗ 复制图片错误 {image_file}: {e}")
                    error_count += 1
            
            success_count += 1
            print(f"  ✓ 文件夹处理完成，已复制 {len(image_files)} 张图片")
                
        except Exception as e:
            print(f"  ✗ 处理文件夹错误: {e}")
            error_count += 1
            
        # 每处理一个文件夹后显示当前统计信息
        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / index if index > 0 else 0
        print(f"当前耗时: {elapsed_time:.2f} 秒, 平均每个文件夹: {avg_time:.2f} 秒")
        print(f"已复制图片: {copied_images} 张\n")
    
    # 最终统计信息
    elapsed_time = time.time() - start_time
    print(f"\n{'='*50}")
    print("复制完成统计:")
    print(f"总文件夹数: {total_folders}")
    print(f"成功处理: {success_count}")
    print(f"跳过: {skip_count}")
    print(f"错误: {error_count}")
    print(f"总图片数: {total_images}")
    print(f"已复制图片: {copied_images}")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每个文件夹: {elapsed_time/total_folders:.2f} 秒" if total_folders > 0 else "无文件夹处理")

# 运行批量复制
if __name__ == "__main__":
    batch_copy_images()