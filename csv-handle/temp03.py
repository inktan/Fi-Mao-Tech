import pandas as pd


# 输入和输出文件路径
input_file = r'y:\GOA-AIGC\02-Model\安装包\stru\ade_20k_语义分割比例数据_03-_.csv'

output_file = r'y:\GOA-AIGC\02-Model\安装包\stru\ade_20k_语义分割比例数据_04-_.csv'

# 读取CSV文件
df = pd.read_csv(input_file)

# 检查id列是否存在
if 'id' not in df.columns:
    raise ValueError("CSV文件中没有找到'id'列")

# 将id列按'_'分割，并扩展为新列
split_data = df['id'].str.split('_', expand=True)

# 检查分割后的列数是否足够
if split_data.shape[1] < 5:
    raise ValueError("id列的分割结果少于5部分，无法满足所有新列")

# 分配新列
df['index'] = split_data[0]
df['road_id'] = split_data[1]
df['longitude'] = split_data[2]
df['latitude'] = split_data[3]
df['date'] = split_data[4]

# 选择要保留的列（包括原始数据中的其他列和新列）
# 如果需要只保留新列，可以使用：new_df = df[['index', 'road_id', 'longitude', 'latitude', 'date']]
# 这里我们保留所有列
new_df = df

# 保存为新的CSV文件
new_df.to_csv(output_file, index=False)

print(f"处理完成，结果已保存到 {output_file}")