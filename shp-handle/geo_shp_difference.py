import geopandas as gpd
import pandas as pd
import os
from pathlib import Path

def merge_and_subtract_shapes():
    # 定义路径
    input_folder = r"E:\work\20250709_sv_michinen\roads"
    road_shp_path = r"e:\work\20250709_sv_michinen\_road.shp"
    output_path = r"E:\work\20250709_sv_michinen\result_road.shp"
    
    try:
        # 1. 读取所有shp文件并合并
        print("正在读取并合并shp文件...")
        shp_files = list(Path(input_folder).glob("*.shp"))
        
        if not shp_files:
            print(f"在路径 {input_folder} 中没有找到shp文件")
            return
        
        print(f"找到 {len(shp_files)} 个shp文件")
        
        # 读取第一个文件作为基础
        gdf_merged = gpd.read_file(shp_files[0])
        
        # 合并其他文件
        for shp_file in shp_files[1:]:
            print(f"正在合并: {shp_file.name}")
            gdf_temp = gpd.read_file(shp_file)
            gdf_merged = pd.concat([gdf_merged, gdf_temp], ignore_index=True)
        
        print(f"合并完成，总共 {len(gdf_merged)} 个要素")
        
        # 2. 读取_road.shp文件
        print("正在读取_road.shp文件...")
        gdf_road = gpd.read_file(road_shp_path)
        print(f"_road.shp 包含 {len(gdf_road)} 个要素")
        
        # 3. 确保所有几何数据使用相同的坐标系
        if gdf_merged.crs != gdf_road.crs:
            print("坐标系不一致，正在统一坐标系...")
            gdf_road = gdf_road.to_crs(gdf_merged.crs)
        
        # 4. 执行几何减法操作
        print("正在执行几何减法操作...")
        
        # 创建_road.shp的联合几何体
        road_union = gdf_road.unary_union
        
        # 从合并的几何体中减去_road.shp的几何体
        gdf_result = gdf_merged.copy()
        gdf_result['geometry'] = gdf_result.geometry.difference(road_union)
        
        # 移除空的几何体
        gdf_result = gdf_result[~gdf_result.is_empty]
        
        print(f"减法操作完成，剩余 {len(gdf_result)} 个要素")
        
        # 5. 保存结果
        print("正在保存结果...")
        gdf_result.to_file(output_path, driver='ESRI Shapefile')
        print(f"结果已保存到: {output_path}")
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

# 运行函数
if __name__ == "__main__":
    merge_and_subtract_shapes()