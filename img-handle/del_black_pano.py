from PIL import Image
# import imagehash
import os
import shutil
import datetime
import time
import sqlite3
import numpy as np
from tqdm import tqdm

# 配置日志
# import logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',
#     handlers=[
#         logging.FileHandler('run_work.log'),  # 日志文件名
#         logging.StreamHandler()  # 控制台输出
#     ]
# )
# logger = logging.getLogger(__name__)
# logger.info('')

Image.MAX_IMAGE_PIXELS = None  # 这将移除像素数量的限制

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录函数开始执行的时间
        result = func(*args, **kwargs)  # 执行原始函数
        end_time = time.time()  # 记录函数结束执行的时间
        elapsed_time = end_time - start_time  # 计算耗时
        print(f"{func.__name__} 耗时: {elapsed_time:.6f} 秒")  # 打印耗时
        return result  # 返回原始函数的结果
    return wrapper


def remove_black_images(img_paths):
    for i, file_path in enumerate(tqdm(img_paths)):
        try:
            image = Image.open(file_path)
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
            # 判断黑色像素比例是否大于0.28
            if black_pixel_ratio > 0.30:
                os.remove(file_path)
                print(file_path)

        except Exception as e:
            continue
            # print(f"删除文件 {file_path} 失败: {e}")

# 使用装饰器
@timer_decorator
def main():
    img_paths = []
    img_names = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

    folder_path_list =[
        r'E:\stree_view',
        ]
    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
                    img_names.append(file)
    print(len(img_paths))
    remove_black_images(img_paths)

if __name__ == '__main__':
    print('a01')
    main()

