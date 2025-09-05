import shutil
import os

# 定义源文件夹和目标文件夹路径
source_folder = r'e:\GoogleDrive\我的云端硬盘\work_fimo\svi_taiwan\sv_pano_410000_420000'
destination_folder = r'e:\svi_panorama\sv_pano_410000_420000'

# 确保目标文件夹存在，如果不存在则创建
os.makedirs(destination_folder, exist_ok=True)

# 复制文件夹
shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)

print(f"Folder copied from {source_folder} to {destination_folder}")
