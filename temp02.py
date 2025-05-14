import pandas as pd

input_file_path = r'e:\work\sv_momo\sv_20250512\street_network_50m_unique_Spatial_Balance.csv'
output_file_path = r'e:\work\sv_momo\sv_20250512\points.csv'

# 加载CSV文件
df = pd.read_csv(input_file_path)

# 在最左侧添加索引列
df.insert(0, 'index', range(len(df)))

# 保存修改后的CSV文件
df.to_csv(output_file_path, index=False)
