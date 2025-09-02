import geopandas as gpd
import pandas as pd

# 读取文件
shp_data = gpd.read_file(r'e:\work\sv_xiufenganning\20250819\街景视觉因子.shp')
csv_data = gpd.read_file(r'e:\work\sv_xiufenganning\20250819\类别情感-逐地点统计.shp')

# 在合并前，将第二个文件的几何列转换为普通列（WKT格式）
# 或者重命名第二个文件的几何列
csv_data = csv_data.rename(columns={'geometry': 'geometry_csv'})

# 合并数据
merged_data = shp_data.merge(csv_data, left_on='地点', right_on='地点', how='left')

# 查看结果
print("合并后的列名:", merged_data.columns.tolist())
print(merged_data.head())

# 方法1：删除多余的几何列（推荐）
# 只保留主要的几何列，将其他几何列转换为普通列或删除
if 'geometry_csv' in merged_data.columns:
    # 可以选择删除或转换为WKT
    merged_data = merged_data.drop(columns=['geometry_csv'])
    print("已删除多余的几何列")

# 方法2：或者将多余的几何列转换为WKT格式
# if 'geometry_csv' in merged_data.columns:
#     merged_data['geometry_csv_wkt'] = merged_data['geometry_csv'].to_wkt()
#     merged_data = merged_data.drop(columns=['geometry_csv'])

# 保存结果
output_path = r"e:\work\sv_xiufenganning\20250819\街景视觉-类别情感.shp"
merged_data.to_file(output_path, driver='ESRI Shapefile', encoding='utf-8')
print(f"合并完成，结果已保存至: {output_path}")

# 验证保存的文件
saved_data = gpd.read_file(output_path)
print("保存文件的信息:")
print(saved_data.info())
print("前几行数据:")
print(saved_data.head())