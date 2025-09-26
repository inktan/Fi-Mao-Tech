import pandas as pd

df = pd.read_csv(r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_7.5_ifference_15.csv')

# 添加从8448929开始的索引列
df['index'] = range(15187240, 15187240 + len(df))

# 或者使用reset_index（如果要从现有索引转换）
# df = df.reset_index()
# df['index'] = df['index'] + 8448929

df.to_csv(r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_7.5_ifference_15.csv', index=False)



