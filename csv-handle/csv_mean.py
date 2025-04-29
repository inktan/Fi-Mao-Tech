import pandas as pd

# 读取两个CSV文件
df1 = pd.read_csv(r'e:\work\sv_shushu\所有指标\ss.csv')  # 替换为第一个文件路径
result_df = df1.groupby(['lon', 'lat'], as_index=False).mean()

# 保存结果到新CSV文件
result_df.to_csv(r'e:\work\sv_shushu\所有指标\ss_mean.csv', index=False)

print("处理完成，结果已保存为 averaged_result.csv")