from PIL import Image
import numpy as np
import csv

from tqdm import tqdm

Image.MAX_IMAGE_PIXELS = None  # 这将移除像素数量的限制

image = Image.open(r'e:\work\苏大-鹌鹑蛋好吃\热力图\contact_transparent_01_L.png').convert('L')  # 确保图像是灰度模式

# 2. 获取图片的宽度和高度
image_width, image_height = image.size

# 3. 定义裁剪窗口的大小
crop_size = 1000  # 1000x1000

# 4. 计算可以切割多少行和列
rows = image_height // crop_size
cols = image_width // crop_size

# 5. 裁剪并保存子图片
for row in range(rows):
    for col in range(cols):
        # 计算每个裁剪块的坐标 (left, upper, right, lower)
        left = col * crop_size
        upper = row * crop_size
        right = left + crop_size
        lower = upper + crop_size
        
        # 裁剪图片
        cropped_image = image.crop((left, upper, right, lower))
        
        # 保存裁剪后的子图片
        cropped_image.save(f'E:\work\苏大-鹌鹑蛋好吃\热力图\c_file\cropped_image_{row}_{col}.png')

print("裁剪并保存图片完成")
