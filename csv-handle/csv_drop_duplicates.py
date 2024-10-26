import pandas as pd

# 使用之前创建的模拟数据
ids_csv_path = r"e:\work\sv_YJ_20240924\all_points.csv"
# data_csv_path = r"e:\work\sv_畫畫_20240923\aomen.csv"
output_csv_path = r"e:\work\sv_YJ_20240924\all_points_01.csv"

# 读取CSV文件
ids_df = pd.read_csv(ids_csv_path)
# data_df = pd.read_csv(data_csv_path)

# 基于id列去重drop_duplicates
# unique_ids = ids_df['Element1'].drop_duplicates()
df_unique = ids_df.drop_duplicates(subset=['input_lat', 'input_lon'])
df_unique.to_csv(output_csv_path, index=False)
# 打印去重后的数据行数
unique_count = df_unique.shape[0]
print(f'去重后共有 {df_unique.shape} 行数据')
print(f'去重后共有 {unique_count} 行数据')

# 使用去重后的id从data.csv中提取数据
# extracted_data = data_df[data_df['OBJECTID'].isin(unique_ids)]

# 保存到新的CSV文件
# extracted_data.to_csv(output_csv_path, index=False)
