import os
import geopandas as gpd
import pandas as pd

shp_paths = []
shp_names = []
accepted_formats = (".shp")

folder_path_list =[
    r'E:\work\sv_xiufenganning\文本分析\netroads'
    ]
for folder_path in folder_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                shp_paths.append(file_path)
                shp_names.append(file)

# shp_paths =[
#     r'e:\work\sv_juanjuanmao\澳门特别行政区\澳门特别行政区_15m_.shp',
#     r'e:\work\sv_shushu\20250423\points.shp',
#     r'e:\work\sv_shushu\20250423\澳门特别行政区_矢量路网\点.shp'
#     ]
# 3. 读取并合并所有 .shp 文件
gdfs = [gpd.read_file(shp) for shp in shp_paths]
print(gdfs)
merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

# 4. 保存合并后的 Shapefile
merged_gdf.to_file(r'E:\work\sv_xiufenganning\文本分析\netroads.shp')
