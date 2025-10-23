import geopandas as gpd
import pandas as pd
from pathlib import Path
import glob

def merge_shp_files(output_path):
    # 查找所有SHP文件
    shp_files = [
        r'e:\work\20250709_sv_michinen\result_road_100m_Spatial.shp',
        r'e:\work\20250709_sv_michinen\pooints.shp',
                 ]
    
    if not shp_files:
        print("未找到SHP文件")
        return
    
    print(f"找到 {len(shp_files)} 个SHP文件")
    
    # 读取所有SHP文件
    gdf_list = []
    for shp_file in shp_files:
        try:
            gdf = gpd.read_file(shp_file)
            gdf['source_file'] = Path(shp_file).name  # 记录来源文件
            gdf_list.append(gdf)
            print(f"已读取: {Path(shp_file).name} - {len(gdf)} 个要素")
        except Exception as e:
            print(f"读取文件 {shp_file} 时出错: {e}")
    
    if not gdf_list:
        print("没有成功读取任何SHP文件")
        return
    
    # 合并所有GeoDataFrame
    merged_gdf = pd.concat(gdf_list, ignore_index=True)
    
    # 保存合并后的文件
    merged_gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"合并完成！总共 {len(merged_gdf)} 个要素")
    print(f"已保存到: {output_path}")
    
    return merged_gdf

# 使用示例
if __name__ == "__main__":
        
    output_file = r"e:\work\20250709_sv_michinen\pooints.shp"  # 输出文件路径
    result = merge_shp_files(output_file)