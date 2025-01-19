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

shp_paths =[r'e:\work\sv_nadingzichidefangtoushi\merged_coordinates_01.shp']  # Replace with your shapefile path

# shp_paths=[r'e:\work\sv_hukejia\sv\handle\points01_panoid02_toshp\merged_output.shp']

# for shp_path in tqdm(shp_paths):
for shp_path in shp_paths:
    gdf = gpd.read_file(shp_path)
    print(shp_path,gdf.shape)
    print(gdf.head)

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


