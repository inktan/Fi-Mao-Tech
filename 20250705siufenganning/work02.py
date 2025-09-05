import os
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString
import warnings
warnings.filterwarnings('ignore')

# 文件路径
shp_a_path = r"e:\work\sv_xiufenganning\20250819\类别情感-逐地点统计.shp"  # 主点文件
shp_b_path = r"e:\work\sv_xiufenganning\20250819\ade_20k_语义分割比例数据_bd09.shp"  # 分析点文件
output_path = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result.shp"

# 读取主点文件
print("正在读取主点文件...")
gdf_main = gpd.read_file(shp_a_path, encoding='gb18030')

# 确保主点文件有几何字段
if 'geometry' not in gdf_main.columns:
    # 假设有经纬度字段，如果没有请根据实际情况修改
    if 'lng' in gdf_main.columns and 'lat' in gdf_main.columns:
        geometry = [Point(xy) for xy in zip(gdf_main['lng'], gdf_main['lat'])]
        gdf_main = gpd.GeoDataFrame(gdf_main, geometry=geometry, crs="EPSG:4326")
    else:
        raise ValueError("主点文件缺少几何信息或经纬度字段")

# 转换坐标系到UTM（用于准确的距离计算）
print("转换坐标系...")
gdf_main = gdf_main.to_crs(epsg=32633)

# 读取分析点文件
print("正在读取分析点文件...")
poi_gdf = gpd.read_file(shp_b_path, encoding='gb18030').to_crs(epsg=32633)

# 识别数值字段（排除几何字段和非数值字段）
numeric_columns = poi_gdf.select_dtypes(include=[np.number]).columns.tolist()
if 'geometry' in numeric_columns:
    numeric_columns.remove('geometry')
print(f"识别的数值字段: {numeric_columns}")

# 存储结果的列表
results = []

# 处理每个主点
print("开始缓冲区分析...")
for index, row in gdf_main.iterrows():
    point = row.geometry
    buffer = point.buffer(1500)  # 500米缓冲区
    
    try:
        # 找到缓冲区内的点
        points_in_buffer = poi_gdf[poi_gdf.geometry.within(buffer)]
        
        # 创建结果行
        result_row = row.to_dict()
        
        # 计算数值字段的平均值
        if len(points_in_buffer) > 0:
            for col in numeric_columns:
                mean_value = points_in_buffer[col].mean()
                result_row[f'{col}'] = mean_value
                # result_row[f'count_{col}'] = len(points_in_buffer)
        else:
            # 如果没有点落在缓冲区内，设置为NaN
            for col in numeric_columns:
                result_row[f'{col}'] = 0
                # result_row[f'count_{col}'] = 0
        
        results.append(result_row)
        
    except Exception as e:
        print(f"处理点 {index} 时出错: {e}")
        # 出错时也添加一个结果行，但设置为NaN
        result_row = row.to_dict()
        for col in numeric_columns:
            result_row[f'{col}'] = 0
            # result_row[f'count_{col}'] = 0
        results.append(result_row)
    
    # 打印进度
    if (index + 1) % 10 == 0:
        print(f"已处理 {index + 1}/{len(gdf_main)} 个点")

# 创建结果GeoDataFrame
print("创建结果文件...")
results_gdf = gpd.GeoDataFrame(results, geometry='geometry', crs=gdf_main.crs)

# 保存结果
print("保存结果...")
results_gdf.to_file(output_path, encoding='gb18030')

print(f"处理完成，结果已保存到: {output_path}")
print(f"总共处理了 {len(results_gdf)} 个点")