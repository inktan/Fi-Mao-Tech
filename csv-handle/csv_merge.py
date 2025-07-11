import pandas as pd
import os

# 获取所有符合模式的文件路径
# csv_paths = []
# csv_names = []
# accepted_formats = (".csv")

# csv_path_list =[
#     r'E:\work\sv_shushu\所有指标\声景',
#     ]
# for folder_path in csv_path_list:
#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             if file.endswith(accepted_formats):
#                 file_path = os.path.join(root, file)
#                 csv_paths.append(file_path)
#                 csv_names.append(file)

# 读取所有 CSV 文件
# 初始化一个空的DataFrame用于存储合并后的数据
combined_df = pd.DataFrame()

# for file in csv_paths:
    # df = pd.read_csv(file, encoding='GBK')
    # df = pd.read_csv(file)
    # need_columns = []
    # for col in df.columns:
        # if not col in combined_df.columns:
        #     need_columns.append(col)
    # 按照列方向进行排序
    # combined_df = pd.concat([combined_df, df[need_columns]], axis=1)

csv_paths=[
    r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\语义分割比例数据_0-_.csv',
    r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\语义分割比例数据_01-_.csv',
    r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\语义分割比例数据_02-_.csv',
]
for file in csv_paths:
    df = pd.read_csv(file)
    # df = pd.read_csv(file, encoding='GBK')
    # print(df.shape)
    # 按照行方向进行排序
    combined_df = pd.concat([combined_df, df])

# combined_df = combined_df.drop_duplicates(subset='img_path')

# # 保存合并后的 DataFrame 到新的 CSV 文件
output_file_path = r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan\ss01.csv'
combined_df.to_csv(output_file_path, index=False)

# print(f"合并后的文件已保存到 {output_file_path}")