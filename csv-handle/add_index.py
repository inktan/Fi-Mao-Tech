import pandas as pd

df = pd.read_csv(r'e:\work\sv_huammengmaomao\冲绳\_network01_25m_unique.csv')

# 添加从8448929开始的索引列
df['index'] = range(27738543, 27738543 + len(df))

# 或者使用reset_index（如果要从现有索引转换）
# df = df.reset_index()
# df['index'] = df['index'] + 8448929

df.to_csv(r'e:\work\sv_huammengmaomao\冲绳\_network01_25m_unique.csv', index=False)



