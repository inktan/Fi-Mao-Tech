import re  
import pandas as pd  
import os
from tqdm import tqdm
import csv 

def remove_non_chinese_chars_from_start(s):  
    pattern = r'^[^\u4e00-\u9fa5]+'  
    return re.sub(pattern, '', s)  
  
def get_all_image_files(base_path):
    # 定义支持的图片文件扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg']
    # 存储找到的图片文件路径
    image_files = set()
    unique_directories = set()

    # 遍历base_path下的所有文件和文件夹
    for root, dirs, files in os.walk(base_path):
        # print(root)
        # continue
    
        for file in files:
            # 检查文件扩展名是否为图片格式
            if any(file.lower().endswith(ext) for ext in image_extensions):
                # 如果是图片文件，添加到列表中
                image_files.add(os.path.join(root, file))
                unique_directories.add(root)

    return image_files,unique_directories


    base_path = r'E:\work\sv_zhoujunling\澳门历史建筑装饰纹样'
    image_files,unique_directories = get_all_image_files(base_path)
    
    # data = pd.DataFrame(columns=['file_path', 'label'])  
    nested_list =[]
    
    for i,file in tqdm(enumerate(image_files)):
        parts = file.split("\\")
        if len(parts) == 7:
            cleaned_string = remove_non_chinese_chars_from_start(parts[5])
            # data.loc[i] = [file, parts[4]+'-'+cleaned_string]
            nested_list.append([file, parts[4]+'-'+cleaned_string])
            
    # unique_items = set(tuple(item) for item in nested_list)  
    filename = base_path+'\\data.csv'
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:  
        writer = csv.writer(file)  
        writer.writerow(['file_path', 'label'])  
        for item in nested_list:  
            writer.writerow(item)  
    # data.to_csv(base_path+'\\data.csv', index=False)  
    
def main01():
    # pass
# if __name__ == '__main__':
    base_path = r'D:\Users\wang.tan.GOA\WeChat Files\wxid_0431434314115\FileStorage\File\2024-08\sv_degree_1200_900'
    image_files,unique_directories = get_all_image_files(base_path)
    
    data = pd.DataFrame(columns=['lng', 'lat'])  
    
    for i,file in tqdm(enumerate(image_files)):
        parts = file.split("_")
        print(parts)
        if len(parts) == 9:
    #         cleaned_string = remove_non_chinese_chars_from_start(parts[5])
            data.loc[i] = [ parts[5], parts[6]]
            
    data.to_csv(base_path+'\\data.csv', index=False)  
    
import sqlite3
import sqlite_vec
from sqlite_vec import serialize_float32
import sqlite3
import sqlite_vec

from typing import List
import struct


def serialize_f32(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)

def main02():

    db = sqlite3.connect(":memory:")
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)

    sqlite_version, vec_version = db.execute(
        "select sqlite_version(), vec_version()"
    ).fetchone()
    print(f"sqlite_version={sqlite_version}, vec_version={vec_version}")

    items = [
        (1, [0.1, 0.1, 0.1, 0.1]),
        (2, [0.2, 0.2, 0.2, 0.2]),
        (3, [0.3, 0.3, 0.3, 0.3]),
        (4, [0.4, 0.4, 0.4, 0.4]),
        (5, [0.5, 0.5, 0.5, 0.5]),
    ]
    query = [0.3, 0.3, 0.3, 0.3]

    db.execute("CREATE VIRTUAL TABLE vec_items USING vec0(embedding float[4])")

    with db:
        for item in items:
            db.execute(
                "INSERT INTO vec_items(rowid, embedding) VALUES (?, ?)",
                [item[0], serialize_f32(item[1])],
            )

    rows = db.execute(
        """
        SELECT
            rowid,
            distance
        FROM vec_items
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT 3
        """,
        [serialize_f32(query)],
    ).fetchall()

    print(rows)
    
def main03():
    db = sqlite3.connect(":memory:")
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    print(db.execute("select vec_version()").fetchone())

    embedding = [0.1, 0.2, 0.3, 0.4]
    result = db.execute('select vec_length(?)', [serialize_float32(embedding)])

    print(result.fetchone()[0]) # 4
        
def main04():
            
    import distutils
    import platform
    import psutil
    import sys

    # Distutils info
    try:
        distutils_info = distutils.__version__
    except AttributeError:
        distutils_info = "distutils version information not available"

    # CPU info
    cpu_info = {
        "Architecture": platform.architecture(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Cores (Physical)": psutil.cpu_count(logical=False),
        "Cores (Logical)": psutil.cpu_count(logical=True)
    }

    # Python installation info
    python_info = {
        "Python Version": platform.python_version(),
        "Python Compiler": platform.python_compiler(),
        "Python Build": platform.python_build(),
        "Python Implementation": platform.python_implementation(),
        "Python Executable": sys.executable
    }

    print("Distutils Info:", distutils_info)
    print("CPU Info:", cpu_info)
    print("Python Installation Info:", python_info)

if __name__ == '__main__':
    main02()