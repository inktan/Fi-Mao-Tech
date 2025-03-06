import pandas as pd
import os

# 定义文件夹路径和文件名模式
folder_path = r'E:\work\sv_juanjuanmao\指标计算\业态混合度'
file_pattern = '.csv'  # 假设文件名为 file1.csv, file2.csv, file3.csv 等

# 获取所有符合模式的文件路径
file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(file_pattern)]

# 读取所有 CSV 文件
# 初始化一个空的DataFrame用于存储合并后的数据
combined_df = pd.DataFrame()

# for file in file_paths:
#     df = pd.read_csv(file, encoding='GBK')
#     need_columns = []
#     for col in df.columns:
#         if not col in combined_df.columns:
#             need_columns.append(col)
#     # 按照列方向进行排序
#     combined_df = pd.concat([combined_df, df[need_columns]], axis=1)

file_paths=[
    r'e:\work\sv_shushu\谷歌\ss_01.csv',
    r'e:\work\sv_shushu\谷歌\ss_02.csv',
    r'e:\work\sv_shushu\谷歌\ss_03.csv',
]
for file in file_paths:
    df = pd.read_csv(file)
    print(df.shape)
    combined_df = pd.concat([combined_df, df])

print(combined_df.columns)
print(combined_df.shape)
print(combined_df.shape)
combined_df = combined_df.drop_duplicates(subset='id')
print(combined_df.shape)

# 保存合并后的 DataFrame 到新的 CSV 文件
output_file_path = 'E:\work\sv_shushu\谷歌\ss_merged_file.csv'
combined_df.to_csv(output_file_path, index=False)

print(f"合并后的文件已保存到 {output_file_path}")