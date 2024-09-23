from PIL import Image
import imagehash
import os
import shutil
import datetime
import time
from tqdm import tqdm

def remove_duplicate_images(img_paths):
    # 创建一个哈希表用于存储图片的哈希值
    hash_table = {}

    # 遍历文件夹中的所有图片文件
    for file_path in tqdm(img_paths):
        img = Image.open(file_path)

        # 计算图片的pHash值
        hash_value = str(imagehash.phash(img))
        # print(hash_value)

        # 如果哈希值已经存在于哈希表中，则说明图片是重复的，删除它或者移动
        # if hash_value in hash_table:
        #     print("删除重复图片:", file_path)
        #     os.remove(file_path)
        # else:
            # 将哈希值添加到哈希表中
            # hash_table[hash_value] = file_path

# 图片库所在文件夹
folder_path = r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\archcollege'

# 获取文件夹中的所有文件信息（含多级的子文件夹）
img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)

remove_duplicate_images(img_paths)
