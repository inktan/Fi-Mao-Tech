import pandas as pd

df = pd.read_csv(r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_15m_unique01.csv')

# 添加从8448929开始的索引列
df['index'] = range(8448929, 8448929 + len(df))

# 或者使用reset_index（如果要从现有索引转换）
# df = df.reset_index()
# df['index'] = df['index'] + 8448929

df.to_csv(r'f:\立方数据\2025年道路数据\【立方数据学社】台湾省\台湾省_15m_unique01.csv', index=False)



