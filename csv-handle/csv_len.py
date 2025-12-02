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
# csv_paths = []
# csv_names = []
# accepted_formats = (".csv")

# csv_path_list =[
#     r'c:\Users\mslne\Desktop\_network01_10m_unique.csv',
#     ]
# for folder_path in csv_path_list:
#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             if file.endswith(accepted_formats):
#                 file_path = os.path.join(root, file)
#                 csv_paths.append(file_path)
#                 csv_names.append(file)
                
csv_paths = [
    r'f:\大数据\poi_北京\北京市2024\csv\北京市_商务住宅_anjuke_01.csv',
    ]
                
for csv_path in csv_paths:
    df = pd.read_csv(csv_path)
    # df = pd.read_csv(csv_path,encoding='gbk')
    print(csv_path)
    print(df.columns)
    print(df.shape)
    print(df.head())
    print(df.tail())

# 查看一个目录下所有CSV文件的行数总和
# def count_csv_rows(directory):
#     total_rows = 0
#     csv_files = []
    
#     # 遍历目录及其子目录
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             if file.endswith(".csv"):
#                 file_path = os.path.join(root, file)
#                 csv_files.append(file_path)
#                 try:
#                     # 使用pandas读取csv以统计数据行（通常会自动排除表头）
#                     # 如果不需要排除表头，可以使用 open(file_path).readlines() 计算
#                     df = pd.read_csv(file_path)
#                     rows = len(df)
#                     print(f"文件: {file_path}, 行数: {rows}")
#                     total_rows += rows
#                 except Exception as e:
#                     print(f"读取 {file_path} 出错: {e}")
                    
#     print(f"\n找到的CSV文件总数: {len(csv_files)}")
#     print(f"所有CSV文件的数据总行数: {total_rows}")
#     return total_rows

# # 在当前目录下执行
# count_csv_rows(r'F:\大数据\2025年8月份道路矢量数据\分城市的道路数据_50m_svinfo_csv')



