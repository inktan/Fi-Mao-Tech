import shutil
import os

# 定义源文件夹和目标文件夹路径
source_folder = r'F:\work\sv_ran\sv_pan\sv_points_surrounding_times01\sv_points_surrounding_times'
destination_folder = r'F:\work\sv_ran\sv_pan'

# 确保目标文件夹存在，如果不存在则创建
os.makedirs(destination_folder, exist_ok=True)

# 移动文件夹
shutil.move(source_folder, destination_folder)
print(f"Folder moved from {source_folder} to {destination_folder}")




