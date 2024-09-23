import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from PIL import Image
import imagehash
import os
import shutil
import datetime
import time
import sqlite3
from tqdm import tqdm

csv_paths = []
csv_names = []
accepted_formats = (".csv")

folder_path_list =[
    r'E:\work\苏大-鹌鹑蛋好吃\热力图\shp_patch',
    # r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\data-20240822',
    ]
for folder_path in folder_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                csv_paths.append(file_path)
                csv_names.append(file)

for i, csv_file in enumerate(tqdm(csv_paths)):
    # if i > 112:
    #     continue
    # if i <= 110:
    #     continue

    # 1. 读取 CSV 文件
    # csv_file = r'e:\work\苏大-鹌鹑蛋好吃\热力图\shp_patch\cropped_image_13_13.csv'  # 替换为你的 CSV 文件路径
    df = pd.read_csv(csv_file)

    latitude_col = 'y'  # 纬度列名
    longitude_col = 'x'  # 经度列名
    df['geometry'] = df.apply(lambda row: Point(row[longitude_col], row[latitude_col]), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf.set_crs(epsg=4326, inplace=True)

    parts = csv_file.split('_')
    num1_y = parts[-2]  # 倒数第二个部分
    num2_x = parts[-1].split('.')[0]  # 最后一个部分，去掉 .png 后缀

    shp_path=csv_file.replace('.csv',f'')

    gdf.to_file(shp_path, driver='ESRI Shapefile')

    print("Shapefile 文件生成成功")
