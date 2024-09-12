from PIL import Image
import imagehash
import os
import shutil
import datetime
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

def get_imagehash(img_paths):
    db_path = r'E:\work\imagehash\imageHash20240830.db'
    db = sqlite3.connect(db_path)

    table_name = 'imageHash'

    cursor = db.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    # 检查查询结果
    table_exists = cursor.fetchone()
    # 如果表存在，则删除它
    if not table_exists:
        db.execute(f'''CREATE TABLE {table_name}
            (ID INTEGER PRIMARY KEY,
            ImageHash TEXT    NOT NULL,
            Path        TEXT    NOT NULL);''')
        db.commit()

    for i, file_path in enumerate(tqdm(img_paths)):
        if i%10000==0:
            db.commit()
# 51 171 238
        logger.info(f'图像查重到第{i}张')

        try:
            img = Image.open(file_path)
            hash_value = str(imagehash.phash(img))

            cursor.execute(f"SELECT * FROM {table_name} WHERE ImageHash=?", (hash_value,))
            if not cursor.fetchone():
                db.execute(f'''INSERT INTO {table_name} (ImageHash, Path)
                            VALUES (?, ?)''', (hash_value, ''))
            else:
                folder_path = os.path.dirname(file_path.replace('data-20240822','data-20240822-dup'))
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                shutil.move(file_path, folder_path)  

        except Exception as e:
            print(e)
            continue

    db.commit()
    db.close()

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
        r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\data-20240822',
        # r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\data-20240822',
        ]
    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
                    img_names.append(file)
    print(len(img_paths))
    # remove_duplicate_images(img_paths)
    # get_imagehash(img_paths)

def SELECT_COUNT():
    db_path = r'E:\work\imagehash\imageHash20240830.db'
    conn = sqlite3.connect(db_path)

    table_name = 'imageHash'
    # 连接到SQLite数据库
    # 数据库文件是test.db，如果文件不存在，会自动在当前目录创建:
    cursor = conn.cursor()

    # 执行查询语句，这里假设表名为example_table:
    cursor.execute('SELECT COUNT(*) FROM imageHash')

    # 使用fetchone()获取单条数据
    count = cursor.fetchone()[0]

    print(f'imageHash 表中共有 {count} 条数据。')

    # 关闭Cursor和Connection:
    cursor.close()
    conn.close()


if __name__ == '__main__':
    print('a01')
    main()

