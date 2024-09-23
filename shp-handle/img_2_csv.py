from PIL import Image
import numpy as np
import csv

from tqdm import tqdm

Image.MAX_IMAGE_PIXELS = None  # 这将移除像素数量的限制

# image = Image.open(r'e:\work\苏大-鹌鹑蛋好吃\热力图\contact_transparent_01_L.png').convert('L')  # 确保图像是灰度模式
image = Image.open(r'e:\work\苏大-鹌鹑蛋好吃\热力图\contact_transparent_02_L.png').convert('L')  # 确保图像是灰度模式
image_array = np.array(image)

# image_array[image_array > 230] = 255

# mask = image_array <= 230
# image_array[mask] = (image_array[mask] / 230 * 99).astype(np.uint8)

# modified_image = Image.fromarray(image_array)

# modified_image.save(r'e:\work\苏大-鹌鹑蛋好吃\热力图\contact_transparent_02_L.png')  # 替换为你想保存的路径


# 获取图像的宽度和高度
height, width = image_array.shape

# 2. 定义 x 和 y 轴的区间
x_min, x_max = 331967.4528198242, 377833.63494873047
y_min, y_max = 3428347.637084961, 3476996.5552368164

# 3. 计算 x 和 y 的映射比例
x_scale = (x_max - x_min) / 10000
y_scale = (y_max - y_min) / 10000


print(x_scale)
print(y_scale)
print()

x_min_start = 0
y_max_start = 0

# 4. 创建 CSV 文件并写入数据
csv_file = r'e:\work\苏大-鹌鹑蛋好吃\热力图\c_file\cropped_image_0_11_file.csv'  # 替换为你想保存的路径
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['x', 'y', 'gray_value'])  # 写入表头

    # 5. 遍历每个像素并映射到 x 和 y 轴坐标
    for i in tqdm(range(height)):
        for j in range(width):
            gray_value = image_array[i, j]

            # 将图像坐标 (i, j) 映射到 x, y 坐标
            x = x_min + j * x_scale
            y = y_max - i * y_scale  # 注意：图像的 y 轴是从上往下的，坐标系是从下往上的

            if gray_value > 230:
                gray_value = 0
            else:
                gray_value = gray_value / 230.0 * 100.0

            writer.writerow([x, y, gray_value])

        if 1==10:
            break

print("CSV 文件生成成功")
