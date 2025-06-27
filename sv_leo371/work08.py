
from tqdm import tqdm
import re
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import os
import shutil

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
    
    for address in ['拉萨', '山南', '林芝']:
        # 读取 Shapefile 文件
        shp_path = f"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines01\{address}市_Function02.shp"
        gdf = gpd.read_file(shp_path)
        gdf = gpd.read_file(shp_path)
        gdf = gdf.to_crs(epsg=32650)
        
        img_paths = []
        img_names = []
        accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

        folder_path01 = f'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_{address}'
        folder_path02 = Path(folder_path01)
        subfolders = [f.name for f in folder_path02.iterdir() if f.is_dir()]

        for index, subfolder_name in tqdm(enumerate(subfolders)):

            parts = subfolder_name.split('_')
            if len(parts)==3:
                lon = parts[1]
                lat = parts[2]

                ubfolder_path = os.path.join(folder_path01, subfolder_name)
                path = Path(ubfolder_path)
                replace_str = path.parent.name

                try:
                    point_coords = (lon, lat)  # 北京天安门坐标
                    nearest_polygon = find_nearest_polygon(point_coords, gdf)
                    dst_dir = ubfolder_path.replace(replace_str,"kmeans\\"+replace_str+'_'+nearest_polygon['Function'])
                    # 复制所有文件
                    try:
                        # 复制整个文件夹（包括子目录和文件）
                        shutil.copytree(ubfolder_path, dst_dir)
                    except Exception as e:
                        print(f"复制失败: {e}")

                except Exception as e:
                    print(f"发生错误: {e}")
                    