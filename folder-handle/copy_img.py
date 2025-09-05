import os
import shutil
from tqdm import tqdm  # 用于显示进度条

def copy_images_with_skip(source_folder, destination_folder):
    """
    单张复制图片到目标文件夹，如果文件已存在则跳过
    
    Args:
        source_folder: 源文件夹路径
        destination_folder: 目标文件夹路径
    """
    # 确保目标文件夹存在
    os.makedirs(destination_folder, exist_ok=True)
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    # 收集所有图片文件
    image_files = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if os.path.splitext(file)[1].lower() in image_extensions:
                image_files.append(os.path.join(root, file))
    
    print(f"找到 {len(image_files)} 张图片")
    
    # 使用进度条复制图片
    copied_count = 0
    skipped_count = 0
    error_count = 0
    
    for src_path in tqdm(image_files, desc="复制图片", unit="张"):
        try:
            # 计算相对路径和目标路径
            rel_path = os.path.relpath(src_path, source_folder)
            dst_path = os.path.join(destination_folder, rel_path)
            
            # 如果目标文件已存在，则跳过
            if os.path.exists(dst_path):
                skipped_count += 1
                continue
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            # 复制文件
            shutil.copy2(src_path, dst_path)
            copied_count += 1
            
        except Exception as e:
            error_count += 1
            print(f"\n复制失败: {src_path} -> {e}")
    
    # 输出统计信息
    print(f"\n复制完成！")
    print(f"成功复制: {copied_count} 张")
    print(f"跳过已存在: {skipped_count} 张")
    print(f"复制失败: {error_count} 张")

# 使用示例
if __name__ == "__main__":
    source_folder = r'e:\GoogleDrive\我的云端硬盘\work_fimo\svi_taiwan\sv_pano_280000_290000'
    destination_folder = r'e:\svi_panorama\sv_pano_280000_290000'
    
    copy_images_with_skip(source_folder, destination_folder)