import os
import shutil
import time
import sqlite3
from tqdm import tqdm

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
# logger.info('')

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录函数开始执行的时间
        result = func(*args, **kwargs)  # 执行原始函数
        end_time = time.time()  # 记录函数结束执行的时间
        elapsed_time = end_time - start_time  # 计算耗时
        print(f"{func.__name__} 耗时: {elapsed_time:.6f} 秒")  # 打印耗时
        return result  # 返回原始函数的结果
    return wrapper

def remove_files(img_paths):
    for i, file_path in enumerate(tqdm(img_paths)):
        try:
            os.remove(file_path)
            print(f"删除文件 {file_path}")
        except Exception as e:
            continue

# 使用装饰器
@timer_decorator
def main():
    img_paths = []
    img_names = []
    accepted_formats = (".jpg")

    folder_path_list =[
        r'E:\work\sv_michinen\sv_pan\_05_sv_extracted_cluster_colors',
        ]
    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
                    img_names.append(file)
    print(len(img_paths))
    remove_files(img_paths)
    
if __name__ == '__main__':
    print('a01')
    main()

