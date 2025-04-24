import geopandas as gpd
from shapely.geometry import Polygon

from tqdm import tqdm
import os

roots = []
shp_names = []
shp_paths = []
accepted_formats = (".shp")
for root, dirs, files in os.walk(r'E:\work\sv_hukejia\sv\handle\points01_panoid03'):
    for file in files:
        if file.endswith(accepted_formats):
            roots.append(root)
            shp_names.append(file)
            file_path = os.path.join(root, file)
            shp_paths.append(file_path)

shp_paths =[r'e:\work\sv_shushu\20250423\all_points01\all_points_Spatial_Balance01.shp']

# for shp_path in tqdm(shp_paths):
for shp_path in shp_paths:
    gdf = gpd.read_file(shp_path)
    print(shp_path,gdf.shape)

    # print(gdf.head)

    # gdf = gdf.drop_duplicates(subset=['osm_id', 'name_2'])
    # print(gdf.shape)
    # print(gdf.head)

    gdf['geometry'] = gdf['geometry'].apply(lambda x: x.wkt)

    # 输出 CSV 文件路径
    csv_file =shp_path.replace('.shp', '.csv')
    # 保存为 CSV 文件
    gdf.to_csv(csv_file, index=False)

    print(f"Shapefile 已成功转换为 CSV 文件：{csv_file}")


