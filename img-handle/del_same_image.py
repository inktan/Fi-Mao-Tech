from PIL import Image
import imagehash
import os
import shutil
import datetime
import time
from tqdm import tqdm

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录函数开始执行的时间
        result = func(*args, **kwargs)  # 执行原始函数
        end_time = time.time()  # 记录函数结束执行的时间
        elapsed_time = end_time - start_time  # 计算耗时
        print(f"{func.__name__} 耗时: {elapsed_time:.6f} 秒")  # 打印耗时
        return result  # 返回原始函数的结果
    return wrapper

def remove_duplicate_images(img_paths):
    hash_table = {}
    for i, file_path in enumerate(tqdm(img_paths)):

        try:
            img = Image.open(file_path)
            hash_value = str(imagehash.phash(img))
            if hash_value in hash_table:
                try:
                    os.remove(file_path)
                    print(f"删除文件 {file_path}")
                except Exception as e:
                    continue
                    # print(f"删除文件 {file_path} 失败: {e}")
            else:
                hash_table[hash_value] = file_path
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
        r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus',
        r'D:\Ai-clip-seacher\AiArchLibAdd-20240822',
        ]
    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
                    img_names.append(file)

    remove_duplicate_images(img_paths)

if __name__ == '__main__':
    main()
