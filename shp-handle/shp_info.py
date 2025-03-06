import geopandas as gpd
from shapely.geometry import Polygon

from tqdm import tqdm
import os
import pandas as pd

roots = []
shp_names = []
shp_paths = []
accepted_formats = (".shp")
for root, dirs, files in os.walk(r'E:\work\sv_juanjuanmao\澳门POI2022\ShapeFile2'):
    for file in files:
        if file.endswith(accepted_formats):
            roots.append(root)
            shp_names.append(file)
            file_path = os.path.join(root, file)
            shp_paths.append(file_path)

shp_paths =[r'e:\work\sv_gonhoo\value_shp\0-Zvalue-Totle-fukuoka-city.shp']

# for shp_path in tqdm(shp_paths):
for shp_path in shp_paths:
    gdf = gpd.read_file(shp_path, encoding='GBK')
    gdf = gpd.read_file(shp_path)
    print(shp_path,gdf.shape)
    print(gdf.head)
    print(gdf.columns)
    print(gdf.crs)

    # # 检查 'name' 列是否存在
    # if 'Name' in gdf.columns:
    #     # 筛选 'name' 列不为 None 的数据
    #     filtered_gdf = gdf[gdf['Name'].notna()]  # 或者使用 gdf['name'] != None
    #     print(f"筛选后的数据行数: {filtered_gdf.shape[0]}")
    #     print(filtered_gdf.head())  # 打印前几行数据
    # else:
    #     print("SHP 文件中没有 'Name' 列")

    # df_unique = gdf.drop_duplicates(subset=['lng', 'lat'])
    # print(df_unique.shape)
    # print(df_unique.head)

    # geometry = gdf.geometry

    # bounding_box = geometry[0].bounds

    # minx, miny, maxx, maxy = bounding_box

    # bottom_left = (minx, miny)
    # bottom_right = (maxx, miny)
    # top_left = (minx, maxy)
    # top_right = (maxx, maxy)

    # print(f"Bottom-left corner: {bottom_left}")
    # print(f"Bottom-right corner: {bottom_right}")
    # print(f"Top-left corner: {top_left}")
    # print(f"Top-right corner: {top_right}")

    # print(gdf.head())


    # for index, row in (gdf.iterrows()):
    #     print(row['geometry'])

def read_shapefile_names(shapefile_path):
    """
    读取Shapefile文件并获取Name列中所有字符串，去重后打印。
    :param shapefile_path: Shapefile文件的路径
    """
    try:
        # 读取Shapefile文件
        # gdf = gpd.read_file(shapefile_path)
        gdf = gpd.read_file(shapefile_path, encoding='GBK')

        str_type = 'page_type'
        # str_type = 'actual_typ'
        # 检查Name列是否存在
        if str_type not in gdf.columns:
            print(f"Shapefile文件中不存在'{str_type}'列。")
            return
        
        # 获取Name列中所有字符串并去重
        unique_names = list(set(gdf[str_type]))
        
        # 打印去重后的Name列
        print("去重后的Name列如下：")
        for name in unique_names:
            print(name)
        print(len(unique_names))

        # 创建DataFrame
        df = pd.DataFrame(unique_names, columns=['page_type'])

        # 保存为CSV文件
        csv_file_path = shapefile_path.replace('.shp', '_names.csv')
        df.to_csv(csv_file_path, index=False)

    
    except Exception as e:
        print(f"读取Shapefile文件时发生错误：{e}")

# 示例使用
# shapefile_path = r'e:\work\sv_gonhoo\fugang\fugang.shp'
# read_shapefile_names(shapefile_path)
