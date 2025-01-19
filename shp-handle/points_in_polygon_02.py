
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm
import os

roots = []
csv_names = []
csv_paths = []
accepted_formats = (".csv")
for root, dirs, files in os.walk(r'E:\work\sv_hukejia\sv\handle\points01_panoid02'):
    for file in files:
        if file.endswith(accepted_formats):
            roots.append(root)
            csv_names.append(file)
            file_path = os.path.join(root, file)
            csv_paths.append(file_path)

# csv_paths =[r'E:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\ai\sv_degree_10_ai\work']

for csv_path in tqdm(csv_paths):
    csv_df = pd.read_csv(csv_path)
    geometry = [Point(xy) for xy in zip(csv_df['longitude'], csv_df['latitude'])]
    gdf_points = gpd.GeoDataFrame(csv_df, geometry=geometry)
    print(gdf_points.shape)
    # 设置坐标参考系统（CRS），通常是WGS84（EPSG:4326）
    gdf_points.set_crs(epsg=4326, inplace=True)

    # 读取第二个shapefile（排除的多边形）
    shapefile_exclude = r'e:\work\sv_hukejia\calculate_point\浙江行政境界高分\行政境界-乡镇-面_街道.shp'
    gdf_polygons = gpd.read_file(shapefile_exclude)

    # 确保多边形和点的坐标参考系统一致
    if gdf_polygons.crs != gdf_points.crs:
        gdf_polygons = gdf_polygons.to_crs(gdf_points.crs)

    # 筛选不在多边形内的点
    gdf_outside_polygons = gpd.overlay(gdf_points, gdf_polygons, how='difference')

    gdf_outside_polygons.to_file(csv_path.replace('points01_panoid02','points01_panoid03').replace('csv','shp'))

    print(gdf_outside_polygons.shape)

    # fig, ax = plt.subplots(1, 1)
    # # # 在画布上绘制第一个 GeoDataFrame 的几何元素
    # gdf_polygons.plot(ax=ax, color='blue')  
    # # # 在同一个画布上绘制第二个 GeoDataFrame 的几何元素
    # gdf_outside_polygons.plot(ax=ax, color='red')  
    # # plt.show()
    # plt.show()
