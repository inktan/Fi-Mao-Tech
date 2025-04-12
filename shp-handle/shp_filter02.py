import pandas as pd

# 1. 读取CSV文件（只加载需要的两列）
input_file = r'e:\work\sv_daxiangshuaishuai\StreetViewSampling\unique_name_2_samples.csv'  # 替换为你的输入文件路径
df = pd.read_csv(input_file, usecols=['osm_id', 'name_2'])

# 2. 检查重复的osm_id
duplicate_counts = df['osm_id'].duplicated(keep=False).sum()
print(f"发现 {duplicate_counts} 行具有重复的osm_id")

# 3. 合并重复项：将相同osm_id的name_2值用逗号连接
merged_df = df.groupby('osm_id')['name_2'].apply(lambda x: ', '.join(str(i) for i in x if pd.notna(i))).reset_index()

# 4. 保存结果
output_file = r'e:\work\sv_daxiangshuaishuai\StreetViewSampling\merge_name_2_.csv'
merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"处理完成，结果已保存到: {output_file}")
print("\n合并后的示例数据：")
print(merged_df.head())