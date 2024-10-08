import pandas as pd
# import geopandas as gpd
# from shapely.geometry import Point
from PIL import Image
# import imagehash
import os
# import shutil
# import datetime
# import time
# import sqlite3
# from tqdm import tqdm

csv_paths = []
csv_names = []
accepted_formats = (".csv")

csv_path_list =[
    r'E:\work\sv_YJ_20240924\points',
    ]
for folder_path in csv_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                csv_paths.append(file_path)
                csv_names.append(file)

# 3. 读取并合并所有 CSV 文件
df_list = [pd.read_csv(csv_file) for csv_file in csv_paths]
merged_df = pd.concat(df_list, ignore_index=True)

# 4. 保存合并后的结果
merged_df.to_csv(r'E:\work\sv_YJ_20240924\all_points.csv', index=False)

print("所有 CSV 文件已合并并保存为 merged_output.csv")
