from PIL import Image
import imagehash
import os
import shutil
import datetime
import time
import sqlite3
from tqdm import tqdm
import ctypes
import sys

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('run_work.log'),  # 日志文件名
        logging.StreamHandler()  # 控制台输出
    ]
)
logger = logging.getLogger(__name__)

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

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def remove_duplicate_images(img_paths):
    hash_table = {}
    for i, file_path in enumerate(tqdm(img_paths)):
        try:
            img = Image.open(file_path)
            hash_value = str(imagehash.phash(img))
            if hash_value in hash_table:
                try:
                    os.remove(file_path)
                    # print(f"删除文件 {file_path}")
                except Exception as e:
                    if not is_admin():
                        print("没有足够的权限删除文件，请以管理员身份运行此脚本。")
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                    else:
                        print("即使以管理员身份运行，也无法删除文件。文件可能被系统或其他程序占用。")
                    # print(f"删除文件 {file_path} 失败: {e}")
                    continue
            else:
                hash_table[hash_value] = file_path
        except Exception as e:
            continue
            # print(f"删除文件 {file_path} 失败: {e}")

# 使用装饰器
@timer_decorator
def main():
    
    # 图片库所在文件夹
    folder_path_list =[
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\archdaily_com-20241012',# 01
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\archdaily_cn-20241012',# 02
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\gooood-20241012',# 03
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\archiposition-20241012',# 04
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\ArchDaily01',# 05
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\ArchDaily',# 06
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\gooood',# 07
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\archiposition',# 08
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\archcollege',# 09
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\Architizer',# 10
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\thad',# 11
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\pinsupinsheji',# 12
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\DSWH',# 13
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\FanTuo'# 14
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\behance'# 15
        r'y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\inplacevisual'# 16
        # r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\data-20240822',
        ]

    # 获取文件夹中的所有文件信息(含多级的子文件夹)
    img_paths = []
    img_names = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
                    img_names.append(file)


    print(len(img_paths))
    remove_duplicate_images(img_paths)
    # get_imagehash(img_paths)

if __name__ == '__main__':
    print('a01')
    main()




