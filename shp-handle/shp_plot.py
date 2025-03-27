import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

folder_path = r'E:\work\苏大-鹌鹑蛋好吃\热力图\shp_patch\cropped_image_14_14'

shp_paths = []
shp_names = []
accepted_formats = (".shp")

folder_path_list =[
    r'E:\work\sv_nadingzichidefangtoushi\澳门路网',
    ]
for folder_path in folder_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                shp_paths.append(file_path)
                shp_names.append(file)

# 3. 读取并合并所有 .shp 文件
shp_paths=[r'e:\work\sv_j_ran\20241227\fish_shp\121.434537_31.1965683_202002.shp']
gdfs = [gpd.read_file(shp) for shp in shp_paths]
# merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
# print(merged_gdf.shape)
# print(merged_gdf.head())

fig, ax = plt.subplots(1, 1)

# 可视化
for i in gdfs:
    i.plot(ax=ax, color='blue')

# fig, ax = plt.subplots(1, 1)
# # 在画布上绘制第一个 GeoDataFrame 的几何元素
# merged_gdf.plot(ax=ax, color='blue')  
# # 在同一个画布上绘制第二个 GeoDataFrame 的几何元素
# gdf_outside_polygons.plot(ax=ax, color='red')  
# plt.show()
plt.show()

