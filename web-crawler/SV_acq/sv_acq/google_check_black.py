from PIL import Image
import numpy as np
import os
from tqdm import tqdm

# 获取文件夹中的所有文件信息（含多级的子文件夹）
img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

for root, dirs, files in os.walk(r'F:\sv_hk_20240521\sv_new'):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)

for image_path in tqdm(img_paths):
    image = Image.open(image_path)
    img_array = np.array(image)
    # 判断黑色像素
    # 对于RGB图像，黑色像素的值为(0, 0, 0)
    # 对于灰度图像，黑色像素的值为0
    if len(img_array.shape) == 3:  # RGB图像
        black_pixels = (img_array == [0, 0, 0]).all(axis=2)
    else:  # 灰度图像
        black_pixels = (img_array == 0)

    num_black_pixels = np.sum(black_pixels)
    total_pixels = img_array.size // 3 if len(img_array.shape) == 3 else img_array.size

    black_pixel_ratio = num_black_pixels / total_pixels
    if black_pixel_ratio > 0.28:
        # [left, upper, right, lower]
        crop_box = (0, 0, 3584, 1663)
        cropped_image = image.crop(crop_box)

        # 放大图片到指定尺寸
        desired_size = (4096, 2048)
        resized_image = cropped_image.resize(desired_size, Image.LANCZOS)

        resized_image.save(image_path)
        # resized_image.show()


