# import pandas as pd
# import os
# import shutil
# # 1. 读取 CSV 文件
# input_file = r'e:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\山南、林芝传统商业街景\score.csv'
# df = pd.read_csv(input_file)

# # 筛选score列大于1的行
# filtered_df = df[df["score"] < 1]
# print(filtered_df)

# target_directory = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\山南、林芝传统商业街景\ai_test'

# # 确保目标文件夹存在
# if not os.path.exists(target_directory):
#     os.makedirs(target_directory)

# # 遍历DataFrame中的每一行
# for index, row in filtered_df.iterrows():
#     # 生成原文件路径
#     original_file_path = os.path.join(r'E:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\山南、林芝传统商业街景\test', row['id']).replace('.txt','.jpg')
#     # 生成目标文件路径
#     target_file_path = os.path.join(target_directory, row['id']).replace('.txt','.jpg')
#     # 移动文件
#     shutil.move(original_file_path, target_file_path)


import pandas as pd

# 读取CSV文件
df = pd.read_csv(r'f:\work\sv_ran\ss_rgb_fisheye_shp\sv_points_surrounding_pd_pf.csv')  # 替换'your_file.csv'为你的文件路径

# 筛选出id列为'住宅a'或'住宅b'的行
filtered_df = df[df['中类'].isin(['别墅区', '住宅区'])]

# 保存为新的CSV文件
filtered_df.to_csv(r'f:\work\sv_ran\ss_rgb_fisheye_shp\sv_points_surrounding_pd_pf01.csv', index=False)  # 替换'filtered_file.csv'为你希望保存的新文件名

