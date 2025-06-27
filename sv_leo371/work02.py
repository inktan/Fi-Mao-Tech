import os
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

# 输入输出路径设置
lines_files = [
    r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines\拉萨市.shp",
    r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines\林芝市.shp",
    r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines\山南市.shp",
]
point_file = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\ss01.shp"
output_dir = r"e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\output_lines_with_avg"
os.makedirs(output_dir, exist_ok=True)

# 读取点数据并检测所有数值列
def detect_numeric_columns(gdf):
    """检测GeoDataFrame中的所有数值列"""
    numeric_cols = []
    for col in gdf.columns:
        if col == 'geometry':
            continue
        if gdf[col].dtype.kind in 'fiu':  # 浮点、整数、无符号整数
            numeric_cols.append(col)
        elif gdf[col].dtype == object:  # 检查是否可以转换为数值
            try:
                pd.to_numeric(gdf[col])
                numeric_cols.append(col)
            except:
                pass
    return numeric_cols

# 读取点数据
points_gdf = gpd.read_file(point_file)
points_gdf = points_gdf[points_gdf.geometry.type == 'Point'].copy()

# 检测所有数值列
numeric_columns = detect_numeric_columns(points_gdf)
if not numeric_columns:
    raise ValueError("点数据中找不到任何数值列，请确保点数据至少包含一个数值属性列")

print(f"检测到数值列: {', '.join(numeric_columns)}")

# 处理每个线文件
for line_file in lines_files:
    # 获取城市名称用于输出文件名
    city_name = os.path.splitext(os.path.basename(line_file))[0]
    output_file = os.path.join(output_dir, f"{city_name}_with_avg.shp")
    
    # 读取线数据
    lines_gdf = gpd.read_file(line_file)
    
    # 为结果准备新列 - 为每个数值列创建平均值列
    lines_gdf['point_count'] = 0  # 记录每条线上的点数
    for col in numeric_columns:
        lines_gdf[f'avg_{col}'] = np.nan  # 为每个数值列创建平均值列
    
    # 如果没有点数据或线数据为空，直接保存
    if len(points_gdf) == 0 or len(lines_gdf) == 0:
        lines_gdf.to_file(output_file)
        continue
    
    # 使用空间连接方法
    joined = gpd.sjoin(points_gdf, lines_gdf, how='inner', predicate='within')
    
    # 分组计算所有数值列的平均值
    if not joined.empty:
        # 首先计算点数
        point_counts = joined.groupby('index_right').size()
        lines_gdf.loc[point_counts.index, 'point_count'] = point_counts
        
        # 然后计算每个数值列的平均值
        for col in numeric_columns:
            avg_values = joined.groupby('index_right')[col].mean()
            lines_gdf.loc[avg_values.index, f'avg_{col}'] = avg_values
    
    # 保存结果
    lines_gdf.to_file(output_file)
    print(f"已处理并保存: {output_file}")

print("所有文件处理完成！")