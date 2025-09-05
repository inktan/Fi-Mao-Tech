import pandas as pd

# 从你之前的代码生成的路径
# csv_path = r'f:\立方数据\2025年道路数据\【立方数据学社】北京市\北京市_50m_Spatial_infos.csv'

# 读取文件
# df = pd.read_csv(csv_path)

# 计算2015年5月的记录数
# count = ((df['year'] == 2016) & (df['month'] == 5)).sum()
# print(f"2016年5月的街景图像记录个数: {count}")
# count = ((df['year'] == 2019) & (df['month'] == 5)).sum()
# print(f"2019年5月的街景图像记录个数: {count}")
# count = ((df['year'] == 2021) & (df['month'] == 5)).sum()
# print(f"2021年5月的街景图像记录个数: {count}")
# count = ((df['year'] == 2023) & (df['month'] == 5)).sum()
# print(f"2023年5月的街景图像记录个数: {count}")

import pandas as pd

# 读取CSV文件（替换为你的文件路径）
csv_path = r'd:\work\sv_yj\0530_5_NY_standpoint_final.csv'
df = pd.read_csv(csv_path)

# 筛选目标年份（2016, 2019, 2021, 2023）
# target_years = [2016, 2019, 2021, 2023]
# df_filtered = df[df['year'].isin(target_years)]

# 按 year 和 month 分组，计算每个组合的记录数
# monthly_counts = df_filtered.groupby(['year', 'month']).size().reset_index(name='count')

# 输出结果
# print(monthly_counts)

# 可选：保存结果到新CSV文件
# monthly_counts.to_csv('monthly_counts_2016_2019_2021_2023.csv', index=False)
# 使用 pivot_table 生成更直观的表格

# pivot_table = df.pivot_table(
    # index='month', 
    # columns='year', 
    # values='pano_id',  # 可以是任意列，仅用于计数
    # aggfunc='count',
#     fill_value=0
# )

# print(pivot_table)
print(df)
print(df.head())
