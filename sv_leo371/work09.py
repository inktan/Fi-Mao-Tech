from tqdm import tqdm
import re
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import os
import shutil
import pandas as pd

def extract_coordinates_from_filename(filename):
    parts = filename.split('\\')
    parts = parts[-2].split('_')
    return float(parts[-2]), float(parts[-1])
    
def find_nearest_polygon(point_coords, gdf):
    # 创建点对象(WGS84坐标系)
    point = Point(point_coords)
    point_gdf = gpd.GeoDataFrame(geometry=[point], crs="EPSG:4326")
    point_gdf = point_gdf.to_crs(epsg=32650)

    # 计算点到每个多边形的距离(单位:米)
    gdf['distance'] = gdf.geometry.distance(point_gdf.geometry[0])
    
    # 找到最近的多边形
    nearest = gdf.loc[gdf['distance'].idxmin()]
    
    # 返回结果(排除几何列和距离列)
    result = nearest.drop(['geometry', 'distance']).to_dict()
    result['distance'] = nearest['distance']  # 单位:米
    
    return result

if __name__ == "__main__":
    # 替换为你的SHP文件路径
    shp_path = r"f:\立方数据\2024年我国多属性建筑矢量数据（免费获取）\合并后的数据（一个省份合并为一个shp文件）\西藏自治区\西藏自治区.shp"
    
    gdf = gpd.read_file(shp_path)
    gdf = gdf.to_crs(epsg=32650)

    ss_paths = [
        # r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\ss_拉萨_a01.csv',
        r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\ss_林芝_a01.csv',
        r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\ss_山南_a01.csv',
    ]
    for ss_path in ss_paths:
        df = pd.read_csv(ss_path)
        # 筛选building;edifice列大于0.39的行
        filtered_df = df[df['building;edifice'] > 0.239]
        # 按id列去重（保留第一个出现的记录）
        deduplicated_df = filtered_df.drop_duplicates(subset=['id'], keep='first')
        print(f"原始数据行数: {len(df)}")
        print(f"筛选后行数: {len(filtered_df)}")
        print(f"去重后行数: {len(deduplicated_df)}")

        # 准备存储结果的列表
        results = []
        geometries = []

        for index, row in tqdm(deduplicated_df.iterrows()):
            img_name = row['id']
            lon, lat = extract_coordinates_from_filename(img_name)
            # print(f"{lon}, {lat}")

            try:
                point_coords = (lon, lat)  # 北京天安门坐标
                nearest_polygon = find_nearest_polygon(point_coords, gdf)

                nearest_info = {
                    'Function': nearest_polygon.get('Function'),
                }
                
                results.append(nearest_info)
                geometries.append(Point(lon, lat))

            except Exception as e:
                print(f"发生错误: {e}")
        
        # 创建GeoDataFrame
        if results and geometries:
            result_df = pd.DataFrame(results)
            result_gdf = gpd.GeoDataFrame(
                result_df,
                geometry=geometries,
                crs="EPSG:4326"
            )
            
            # 保存为shapefile
            output_shp = ss_path.replace('_a01.csv', '_Function.shp')
            result_gdf.to_file(output_shp, encoding='utf-8')
            print(f"结果已保存到: {output_shp}")



