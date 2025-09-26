import pandas as pd

# 读取两个CSV文件
df1 = pd.read_csv(r'd:\work\sv_yj\sv_phoenix\merged_data_id.csv')
df2 = pd.read_csv(r'd:\work\sv_yj\sv_phoenix\merged_data_02_id.csv')

# 设置索引为pano_panoid
df1 = df1.set_index('img_id')
df2 = df2.set_index('img_id')

# 使用combine_first，df2的值会优先于df1
result = df2.combine_first(df1)

# 重置索引
result = result.reset_index()

output_file_path = r'd:\work\sv_yj\sv_phoenix\merged_data_03.csv'
result.to_csv(output_file_path, index=False)

print(f"合并后的文件已保存到 {output_file_path}")
