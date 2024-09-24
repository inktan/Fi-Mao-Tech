import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

folder_path = r'E:\work\苏大-鹌鹑蛋好吃\热力图\shp_patch\cropped_image_14_14'

shp_paths = []
shp_names = []
accepted_formats = (".shp")

folder_path_list =[
    r'E:\work\苏大-鹌鹑蛋好吃\热力图\shp_patch\cropped_image_13_14',
    r'E:\work\苏大-鹌鹑蛋好吃\热力图\shp_patch\cropped_image_14_14',
    # r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\data-20240822',
    ]
for folder_path in folder_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                shp_paths.append(file_path)
                shp_names.append(file)

# 3. 读取并合并所有 .shp 文件
gdfs = [gpd.read_file(shp) for shp in shp_paths]
merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

# 可视化
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
merged_gdf.plot(ax=ax)
plt.show()
