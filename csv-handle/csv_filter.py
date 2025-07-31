import pandas as pd

# 读取CSV文件
df = pd.read_csv(r'f:\立方数据\2025年道路数据\【立方数据学社】北京市\北京市_50m_Spatial_infos01.csv')  # 替换为你的CSV文件路径

# 筛选year列为2021的数据
df_2021 = df[df['year'] == 2021]

# 保存为新的CSV文件
df_2021.to_csv(r'f:\立方数据\2025年道路数据\【立方数据学社】北京市\北京市_50m_Spatial_infos_2021.csv', index=False)  # index=False表示不保存行索引




