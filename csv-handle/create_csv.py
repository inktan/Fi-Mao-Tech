import os
import csv
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # 这将移除像素数量的限制

def get_all_image_files(base_path):
    # 定义支持的图片文件扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg']
    # 存储找到的图片文件路径
    image_files = set()
    unique_directories = set()

    # 遍历base_path下的所有文件和文件夹
    for root, dirs, files in os.walk(base_path):
        for file in files:
            # 检查文件扩展名是否为图片格式
            if any(file.lower().endswith(ext) for ext in image_extensions):
                # 如果是图片文件，添加到列表中
                # image_files.add(os.path.join(root, file))
                image_files.add(file)
                unique_directories.add(root)

    return image_files,unique_directories

image_files,unique_directories = get_all_image_files(r'E:\work\sv_畫畫_20240923\sv_degrees')

split_file_names = []

# 遍历文件名，分割并存储到列表中
for file_name in image_files:
    split_elements = file_name.split('_')
    split_file_names.append(split_elements)

# 创建CSV文件并写入数据
csv_file_path = r"E:\work\sv_畫畫_20240923/output.csv"
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    # 写入标题行
    writer.writerow(['Element1', 'Element2', 'Element3', 'Element4', 'Element5'])
    # 写入数据
    for item in split_file_names:
        writer.writerow(item)

# csv_file_path  # 显示CSV文件的路径（模拟环境，实际路径需要根据实际情况设置）
