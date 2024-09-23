from PIL import Image
import numpy as np
import csv
import os
from tqdm import tqdm

Image.MAX_IMAGE_PIXELS = None

x_min, x_max = 331967.4528198242, 377833.63494873047
y_min, y_max = 3428347.637084961, 3476996.5552368164

# 3. 计算 x 和 y 的映射比例
x_scale = (x_max - x_min) / 21.0
y_scale = (y_max - y_min) / 22.0

print(x_scale)
print(y_scale)
print()

img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

folder_path_list =[
    r'E:\work\苏大-鹌鹑蛋好吃\热力图\png_patch',
    # r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\data-20240822',
    ]
for folder_path in folder_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)

for i, file_path in enumerate(tqdm(img_paths)):
    # if i > 112:
    #     continue
    # if i <= 110:
    #     continue

    parts = file_path.split('_')
    num1_y = int(parts[-2])  # 倒数第二个部分
    num2_x = int(parts[-1].split('.')[0])  # 最后一个部分，去掉 .png 后缀
    csv_file = file_path.replace('png_patch','shp_patch').replace('.png', '.csv')

    if os.path.exists(csv_file):
        print(f"{csv_file} 已存在，跳过当前循环")
        continue  # 跳过当前循环

    x_min_start = x_min + num2_x * x_scale
    y_max_start = y_max - num1_y * y_scale

    image = Image.open(file_path).convert('L')  # 确保图像是灰度模式
    image_array = np.array(image)
    # 获取图像的宽度和高度
    height, width = image_array.shape

    # 3. 计算 x 和 y 的映射比例
    x_scale_patch = x_scale / width
    y_scale_patch = y_scale / height

    print(x_scale_patch)
    print(y_scale_patch)

    # 4. 创建 CSV 文件并写入数据
    csv_file = file_path.replace('png_patch','shp_patch').replace('.png', '.csv')
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['x', 'y', 'gray_value'])  # 写入表头

        # 5. 遍历每个像素并映射到 x 和 y 轴坐标
        for i in tqdm(range(height)):
            for j in range(width):
                gray_value = image_array[i, j]

                # 将图像坐标 (i, j) 映射到 x, y 坐标
                x = x_min_start + j * x_scale_patch
                y = y_max_start - i * y_scale_patch  # 注意：图像的 y 轴是从上往下的，坐标系是从下往上的

                if gray_value <= 230:
                    gray_value = gray_value / 230.0 * 100.0
                    writer.writerow([x, y, gray_value])

    print("CSV 文件生成成功")
