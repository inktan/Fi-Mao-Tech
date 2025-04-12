import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union
from geopy.distance import geodesic
from tqdm import tqdm
import os
import pandas as pd

def load_shapefile(file_path):
    """Load a shapefile and return a GeoDataFrame."""
    gdf = gpd.read_file(file_path)
    return gdf

def filter_points(gdf, min_distance_meters=49):
    """Filter points to ensure the minimum distance between any two points."""

    # 创建一个空的GeoDataFrame来存储剩余的点
    remaining_points_gdf = gpd.GeoDataFrame(columns=gdf.columns)  # 保持与gdf相同的列名
    remaining_points_gdf.set_geometry('geometry', inplace=True)  # 确保geometry列被识别为几何列
 
    for idx, row in tqdm(gdf.iterrows()):
        if remaining_points_gdf.empty:
            # 如果remaining_points_gdf为空，直接添加当前点
            remaining_points_gdf = remaining_points_gdf._append(row, ignore_index=True)
            print(remaining_points_gdf.head())
            continue

        # 计算每个点到随机点的距离
        point = row['geometry']
        remaining_points_gdf['distance'] = remaining_points_gdf['geometry'].apply(lambda geom: geom.distance(point))

        # 找到距离新点最近的点
        nearest_point_index = remaining_points_gdf['distance'].idxmin()
        nearest_distance = remaining_points_gdf.loc[nearest_point_index, 'distance']
 
        print(nearest_distance)
        # 如果最近距离大于最小距离，则添加新点
        if nearest_distance > min_distance_meters or nearest_distance < 0.1:
            remaining_points_gdf = remaining_points_gdf._append(row, ignore_index=True)
 
        # 清理distance列，因为它只用于临时计算
        remaining_points_gdf.drop(columns=['distance'], inplace=True)
 
    remaining_points_gdf.set_crs(epsg=32633, inplace=True)  # Assuming WGS84
    if remaining_points_gdf.crs != {'init': 'epsg:4326'}:
        remaining_points_gdf = remaining_points_gdf.to_crs(epsg=4326)

    return remaining_points_gdf

def main(shapefile_path):
    # Load shapefile
    gdf = load_shapefile(shapefile_path)
    
    # Ensure the coordinates are in WGS84 (EPSG:4326)
    if gdf.crs != {'init': 'epsg:4326'}:
        gdf = gdf.to_crs(epsg=4326)
    
    # 这里假设是UTM区域33N（EPSG:32633），你需要根据实际情况替换
    utm_crs = 'EPSG:32633'  # 替换为你的UTM区域
    gdf = gdf.to_crs(utm_crs)

    # Filter points to ensure minimum distance
    filtered_gdf = filter_points(gdf)
    
    # Save the result to a new shapefile
    output_path = shapefile_path.replace('.shp', '0m.shp')
    filtered_gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"Filtered points saved to {output_path}")

if __name__ == "__main__":
    shapefile_path = r'e:\work\sv_daxiangshuaishuai\StreetViewSampling\18_SZParks_300_Rd_50m_.shp'  # Replace with your shapefile path
    main(shapefile_path)