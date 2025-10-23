import pandas as pd
import os

# 设置显示选项
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_rows', None)     # 显示所有行
pd.set_option('display.float_format', '{:.10f}'.format)  # 设置浮点数显示精度
pd.set_option('display.width', None)        # 自动调整显示宽度
pd.set_option('display.max_colwidth', None) # 显示完整的列内容

# 设置 pandas 显示选项，让所有列在一行显示
pd.set_option('display.expand_frame_repr', False)  # 禁止换行显示

# 或者更简单的方式，设置一个足够大的宽度
# pd.set_option('display.width', 1000)

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

# 读取CSV文件（替换为你的文件路径）
# csv_path = r'd:\work\sv_yj\0920\0530_5_NY_standpoint_final_with_image_id.csv'
# df = pd.read_csv(csv_path)

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
# print(df)
# print(df.shape)
# print(df.head())

# csv_path =  r'd:\work\sv_yj\sv_houston\Houston_with_gl_05.csv'
# df = pd.read_csv(csv_path)
# print(df.shape)
# print(df.head())

# 获取所有符合模式的文件路径
csv_paths = []
csv_names = []
accepted_formats = (".csv")

csv_path_list =[
    r'E:\work\sv_YJ\sv_20250901',
    ]
for folder_path in csv_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                csv_paths.append(file_path)
                csv_names.append(file)
                
csv_paths = [
    r'e:\work\20250709_sv_michinen\20251021\points_suply01.csv',
    ]
                
for csv_path in csv_paths:
    df = pd.read_csv(csv_path)
    print(csv_path)
    # print(df.columns)
    print(df.shape)
    print(df.head())
    print(df.tail())
    
    
    
    
    
    