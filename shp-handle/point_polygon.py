from tqdm import tqdm
import re
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import os
import shutil

img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

folder_path = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街景建筑分类_bs'

for root, dirs, files in os.walk(folder_path):
    for filename in files:
        if filename.endswith(accepted_formats):
            file_path = os.path.join(root, filename)
            img_paths.append(file_path)
            img_names.append(filename)

def extract_coordinates_from_filename(filename):
    """
    从文件名中提取经纬度信息
    文件名格式示例：34981_94.35798215720_29.65231410060_201310_180.jpg
    """
    # 使用正则表达式提取两个浮点数（经度和纬度）
    pattern = r'_(\d+\.\d+)_(\d+\.\d+)_'
    match = re.search(pattern, filename)
    if match:
        lon = float(match.group(1))
        lat = float(match.group(2))
        return lon, lat
    else:
        raise ValueError("无法从文件名中提取经纬度信息")
    

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
        
    for index, img_name in tqdm(enumerate(img_names)):

        if len(img_name.split('_'))==5:
            lon, lat = extract_coordinates_from_filename(os.path.basename(img_name))
            print(f"{lon}, {lat}")
            # print(f"{img_paths[index]}提取的经纬度: 经度={lon}, 纬度={lat}")

            path = Path(img_paths[index])
            replace_str = path.parent.parent.name

            try:
                point_coords = (lon, lat)  # 北京天安门坐标
                
                nearest_polygon = find_nearest_polygon(point_coords, gdf)

                parent_dir01 = os.path.dirname(img_paths[index])
                dst_dir = parent_dir01.replace(replace_str,nearest_polygon['Function'])

                # 确保目标目录存在
                # os.makedirs(dst_dir, exist_ok=True)

                # 复制所有文件
                try:
                    # 复制整个文件夹（包括子目录和文件）
                    shutil.copytree(parent_dir01, dst_dir)
                except Exception as e:
                    print(f"复制失败: {e}")

            except Exception as e:
                print(f"发生错误: {e}")
                