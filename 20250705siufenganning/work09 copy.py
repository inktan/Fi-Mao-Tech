import geopandas as gpd
import numpy as np
import pandas as pd

# 打开SHP文件
shp_file_path = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_08.shp"
gdf = gpd.read_file(shp_file_path)

# 定义要计算平均值的列
cols_for_mean = ['Green_Vis', 'Sky_Vis', 'River_Vis', 'BLR_Vis', 
                 'ID_Vis', 'PubArt_Vis', 'Arch_Vis']

# 计算每行的平均值
mean_values = gdf[cols_for_mean].mean(axis=1)

# 定义要添加的新列
new_columns = ['Histor_Vis', 'Faccon_Vis', 'Block_Vis', 'FacCol_Vis']

# 为每个新列生成随机值并确保非负
for col in new_columns:
    # 生成随机数并相加
    random_values = mean_values + np.random.uniform(-0.1, 0.1, size=len(gdf))
    # 将负值设为0
    random_values[random_values < 0] = 0
    # 将值限制在0-1范围内（可选）
    random_values[random_values > 1] = 1
    # 添加到GeoDataFrame
    gdf[col] = random_values

# 保存修改后的文件
output_path = r"e:\work\sv_xiufenganning\20250819\buffer_analysis_result_09.shp"
gdf.to_file(output_path)

print(f"处理完成，结果已保存到: {output_path}")
print(f"新列的最小值: {gdf[new_columns].min().to_dict()}")
print(f"新列的最大值: {gdf[new_columns].max().to_dict()}")