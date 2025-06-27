

import os
import shutil
import geopandas as gpd
from shapely.geometry import Point

def process_lines_and_folders(line_shp_path, source_folder, output_base_folder):
    """
    处理line shp文件和源文件夹，根据距离匹配将子文件夹复制到对应的class文件夹中
    
    参数:
        line_shp_path: line shapefile路径
        source_folder: 包含子文件夹的源文件夹路径
        output_base_folder: 输出基础文件夹路径
    """
    # 读取line shapefile
    lines_gdf = gpd.read_file(line_shp_path)
    
    # 确保输出基础文件夹存在
    os.makedirs(output_base_folder, exist_ok=True)
    
    # 遍历源文件夹中的所有子文件夹
    for root, dirs, files in os.walk(source_folder):
        for dir_name in dirs:
            # 分割子文件夹名称
            parts = dir_name.split('_')
            if len(parts) < 2:
                print(f"跳过文件夹 {dir_name}，名称不符合要求")
                continue
                
            # 获取最后两个元素作为坐标
            try:
                x, y = map(float, parts[-2:])
            except ValueError:
                print(f"跳过文件夹 {dir_name}，无法解析坐标")
                continue
                
            # 创建点
            point = Point(x, y)
            
            # 查找距离最近(几乎为0)的line
            matched_class = None
            min_distance = float('inf')
            
            for idx, line in lines_gdf.iterrows():
                distance = point.distance(line.geometry)
                if distance < min_distance:
                    min_distance = distance
                    matched_class = line['cluster']  # 假设属性字段名为'class'
            
            # 如果找到距离几乎为0的line
            if min_distance < 1e-6:  # 设置一个很小的阈值
                # 创建class文件夹(如果不存在)
                class_folder = os.path.join(output_base_folder, str(matched_class))
                os.makedirs(class_folder, exist_ok=True)
                
                # 源子文件夹路径
                src_folder_path = os.path.join(root, dir_name)
                # 目标路径
                dst_folder_path = os.path.join(class_folder, dir_name)
                
                # 复制文件夹
                try:
                    if not os.path.exists(dst_folder_path):
                        shutil.copytree(src_folder_path, dst_folder_path)
                        print(f"复制 {dir_name} 到 class {matched_class} 文件夹")
                    else:
                        print(f"跳过 {dir_name}，目标已存在")
                except Exception as e:
                    print(f"复制 {dir_name} 时出错: {str(e)}")
            else:
                print(f"文件夹 {dir_name} 没有匹配到任何line (最小距离: {min_distance})")

# 使用示例
if __name__ == "__main__":
    # line_shp_path = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines_kmeans_class\拉萨市.shp"  # 替换为你的line shapefile路径
    # source_folder = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_拉萨'
    # output_base_folder = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\kmeans_拉萨"     # 替换为输出基础文件夹路径

    # line_shp_path = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines_kmeans_class\山南市.shp"  # 替换为你的line shapefile路径
    # source_folder = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_山南'
    # output_base_folder = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\kmeans_山南"     # 替换为输出基础文件夹路径

    line_shp_path = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines_kmeans_class\林芝市.shp"  # 替换为你的line shapefile路径
    source_folder = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\sv_林芝'
    output_base_folder = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\kmeans_林芝"     # 替换为输出基础文件夹路径

    
    process_lines_and_folders(line_shp_path, source_folder, output_base_folder)