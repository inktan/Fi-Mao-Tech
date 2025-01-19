import shutil
import os

# 定义源文件夹和目标文件夹路径
source_folder = r'F:\sv_shanghai\20220720-上海\sv_pan\BaiduSyncdisk01\SH-2'
destination_folder = r'D:\work\sv_shanghai'

# 确保目标文件夹存在，如果不存在则创建
os.makedirs(destination_folder, exist_ok=True)

# 移动文件夹
shutil.move(source_folder, destination_folder)
print(f"Folder moved from {source_folder} to {destination_folder}")



