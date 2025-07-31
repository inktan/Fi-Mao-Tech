import geopandas as gpd
import pandas as pd

# 读取文件
shp_data = gpd.read_file(r'f:\立方数据\2025年道路数据\【立方数据学社】北京市\北京市.shp')

# 删除多余的id列（如果需要）
shp_data = shp_data.drop(columns=['id'])

# 查看结果
print(shp_data.head())

# 保存结果（可选）
output_path = r"f:\立方数据\2025年道路数据\【立方数据学社】北京市\北京市.shp"

# merged_data = shp_data
shp_data.to_file(output_path, encoding="utf-8")
print(f"合并完成，结果已保存至: {output_path}")


