import pandas as pd

# 1. 读取 CSV 文件
input_file = r'e:\work\sv_畫畫_20240923\aomen_sv_info.csv'
df = pd.read_csv(input_file)

length_of_csv = len(df)

print(length_of_csv)

# import pandas as pd

# df = pd.read_csv(r'e:\work\sv_YJ_20240924\all_points.csv')
# df_unique = df.drop_duplicates(subset='pano_id')
# print(f'去重后共有 {df_unique.shape[0]} 行数据')


