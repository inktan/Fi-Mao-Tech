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
    r'E:\work\sv_juanjuanmao\指标计算',
    ]
for folder_path in folder_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                csv_paths.append(file_path)
                csv_names.append(file)

# csv_paths = [r'e:\work\sv_juanjuanmao\window_ss.csv']

for i, csv_file in enumerate(tqdm(csv_paths)):
    # if i > 112:
    #     continue
    # if i <= 110:
    #     continue

    df = pd.read_csv(csv_file)

    df['geometry'] = df.apply(lambda row: Point(float(row['longitude']), float(row['latitude'])), axis=1)
    # df['geometry'] = df.apply(lambda row: Point(float(row['longitude']), float(row['latitude'])), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf.set_crs(epsg=4326, inplace=True)

    shp_path=csv_file.replace('points01_panoid02','points01_panoid02_toshp').replace('.csv','.shp')

    gdf.to_file(shp_path, driver='ESRI Shapefile')

    print("Shapefile 文件生成成功")
