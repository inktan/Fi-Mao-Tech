import shutil
import os

# 源目录和目标目录
# 117gb
# source_dir = r"F:\stree_view\tar_0662"
# # 317gb
# source_dir = r"F:\stree_view\tar_0772"
# # 354gb
# source_dir = r"F:\stree_view\tar_0552"


source_dirs =[
r"F:\stree_view\tar_0662",
r"F:\stree_view\tar_0772",
r"F:\stree_view\tar_0552",
    ]

target_dir = r"E:\stree_view\tar_0881"

for source_dir in source_dirs:


    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)

    # 移动所有文件
    for filename in os.listdir(source_dir):
        source_path = os.path.join(source_dir, filename)
        target_path = os.path.join(target_dir, filename)
        try:
                
            # 如果是文件则移动
            if os.path.isfile(source_path):
                print(source_path)
                print(target_path)
                print('start')
                shutil.move(source_path, target_path)
        except :
            continue