import pandas as pd
category = 'wealthy'

# 假设df是你的DataFrame，且有一个名为'id'的列
df = pd.read_csv(f'e:\work\sv_畫畫_20240923\csv_results\ss_0.csv')

df = df.drop('id', axis=1)

# 计算每个id的平均值
average_df = df.groupby("iamge_name").mean()

# 保存为新的CSV文件
average_df.to_csv(f"e:\work\sv_畫畫_20240923\csv_results\ss_1.csv")

