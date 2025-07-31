import geopandas as gpd
import pandas as pd

# 1. 读取SHP文件
input_shp =  r'e:\work\sv_xiufenganning\地理数据\Export_Output_4_svi_data_gcj_03.shp'  # 替换为你的输入文件路径
output_shp =  r'e:\work\sv_xiufenganning\地理数据\Export_Output_4_svi_data_gcj_04.shp' # 替换为你想要的输出路径

gdf = gpd.read_file(input_shp)

# 2. 检查必要列是否存在
# required_columns = ['id', 'complexity', 'harmony', 'geometry']
# for col in required_columns:
#     if col not in gdf.columns:
#         raise ValueError(f"缺少必要列: {col}")

# 3. 按非几何列分组并计算数值列的平均值
required_columns = gdf.select_dtypes(include=['int64', 'float64']).columns.tolist()  # 获取所有数值列
required_columns.remove('no')  # 移除几何列（如果被误识别为数值列）
# 3. 按ID分组计算平均值
# 首先复制几何列，因为groupby会丢失几何信息
temp_df = gdf.copy()

# 计算数值列的平均值
avg_values = temp_df.groupby('no')[required_columns].mean().reset_index()

# 获取每个ID组的第一个几何图形（或可以根据需要选择其他策略）
first_geometries = temp_df.groupby('no')['geometry'].first().reset_index()

# 合并平均值和几何图形
result_gdf = pd.merge(avg_values, first_geometries, on='no', how='left')

# 转换回GeoDataFrame
result_gdf = gpd.GeoDataFrame(result_gdf, geometry='geometry', crs=gdf.crs)

# 4. 保留原始数据的所有属性列（可选）
# 如果需要保留其他列的第一个值
# other_columns = [col for col in gdf.columns if col not in ['id','complexity', 'degree', 'harmony', 'geometry']]
# for col in other_columns:
#     first_values = temp_df.groupby('id')[col].first().reset_index()
#     result_gdf = pd.merge(result_gdf, first_values, on='id', how='left')

# 5. 保存结果
result_gdf.to_file(output_shp, encoding='utf-8')
print(f"处理完成，结果已保存至: {output_shp}")

# 打印处理摘要
print("\n处理摘要:")
print(f"原始记录数: {len(gdf)}")
print(f"处理后记录数: {len(result_gdf)}")
print("示例结果:")
print(result_gdf.head())