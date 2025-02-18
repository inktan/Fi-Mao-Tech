import pandas as pd

ids_csv_path = r'e:\work\sv_welly\语义分析指标_merged_file.csv'
ids_df = pd.read_csv(ids_csv_path)
unique_count = ids_df.shape[0]
print(f'原数据有 {ids_df.shape} 行数据')

# df_unique = ids_df.drop_duplicates(subset=['longitude', 'latitude'])
df_unique = ids_df.drop_duplicates(subset=['img_path'])
# 打印去重后的数据行数
print(f'去重后共有 {df_unique.shape} 行数据')

output_csv_path = r"e:\work\sv_welly\语义分析指标_merged_file.csv"
df_unique.to_csv(output_csv_path, index=False)







