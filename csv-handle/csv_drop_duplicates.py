import pandas as pd

# ids_csv_path = r'Y:\GOA-AIGC\02-Model\安装包\stru\sv_拉萨_brightness_saturation.csv'

# ids_df = pd.read_csv(ids_csv_path)
# print(ids_df)
# print(ids_df.iloc[0,0])
# unique_count = ids_df.shape[0]
# print(f'原数据有 {ids_df.shape} 行数据')

# # df_unique = ids_df.drop_duplicates(subset=['longitude', 'latitude'])
# df_unique = ids_df.drop_duplicates(subset=['path'])
# # 打印去重后的数据行数
# print(f'去重后共有 {df_unique.shape} 行数据')

# output_csv_path =  r'Y:\GOA-AIGC\02-Model\安装包\stru\sv_拉萨_brightness_saturation01.csv'
# df_unique.to_csv(output_csv_path, index=False)

ids_csv_path = r'Y:\GOA-AIGC\02-Model\安装包\stru\sv_拉萨_brightness_saturation.csv'

# 读取CSV文件
df = pd.read_csv(ids_csv_path)

# 假设列名是 "id"，使用 _ 分割并保留最后一个元素
df["path"] = df["path"].str.split("\\").str[-1]
print(df.iloc[0,0])

output_csv_path =  r'Y:\GOA-AIGC\02-Model\安装包\stru\sv_拉萨_brightness_saturation02.csv'

df.to_csv(output_csv_path, index=False)

# 查看结果
print(df)