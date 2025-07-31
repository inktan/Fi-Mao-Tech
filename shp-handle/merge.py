import geopandas as gpd
import pandas as pd

# 读取文件
shp_data = gpd.read_file(r'e:\work\sv_xiufenganning\地理数据\Export_Output_4_svi_data_gcj_02.shp')
csv_data = pd.read_csv(r'e:\work\sv_xiufenganning\地理数据\harmony_results_01.csv')

# 合并数据
merged_data = shp_data.merge(csv_data, left_on='no', right_on='id', how='left')

# 查看结果
print(merged_data.head())

# 保存结果（可选）
output_path = r"e:\work\sv_xiufenganning\地理数据\Export_Output_4_svi_data_gcj_03.shp"

# merged_data = shp_data
merged_data.to_file(output_path, encoding="utf-8")
print(f"合并完成，结果已保存至: {output_path}")


