import pandas as pd

input_file = r'e:\work\sv_daxiangshuaishuai\StreetViewSampling\18_SZParks_300_Rd_50m_.csv'  # 替换为你的输入文件路径
df = pd.read_csv(input_file)

unique_values = df['osm_id'].unique()
print(f"找到 {len(unique_values)} 个唯一值")

# 4. 对每个唯一值抽取3行样本（如果存在足够数据）
samples = []
for value in unique_values:
    subset = df[df['osm_id'] == value]
    # 如果该值的行数>=3则取3行，否则取全部
    sample_size = min(3, len(subset))
    samples.append(subset.sample(sample_size) if sample_size > 0 else subset)

# 5. 合并所有样本并保存
result_df = pd.concat(samples)
output_csv = r'e:\work\sv_daxiangshuaishuai\StreetViewSampling\18_SZParks_300_Rd_50m_osm_id_samples.csv'
result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"已提取 {len(result_df)} 行样本数据，保存到: {output_csv}")
print("示例数据：")
print(result_df[['name_2'] + list(result_df.columns[:3])].head())  # 显示前几列





