import geopandas as gpd
import pandas as pd

# 读取文件
shp_data = gpd.read_file(r'e:\work\sv_xiufenganning\20250819\街景视觉-类别情感01.shp')

# 删除多余的id列（如果需要）
shp_data = shp_data.drop(columns=['地址_y'])
# shp_data = shp_data.drop(columns=['id'])

# 查看结果
print(shp_data.head())

# 保存结果（可选）
output_path = r"e:\work\sv_xiufenganning\20250819\街景视觉-类别情感02.shp"

# merged_data = shp_data
shp_data.to_file(output_path, encoding="utf-8")
print(f"合并完成，结果已保存至: {output_path}")


