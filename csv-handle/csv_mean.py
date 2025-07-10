import pandas as pd

# 读取两个CSV文件
df = pd.read_csv(r'e:\work\sv_xiufenganning\地理数据\ade_20k_语义00分割比例数据_03-_.csv')  # 替换为第一个文件路径
df = df.drop(columns=['lon'])
df = df.drop(columns=['lat'])
df = df.drop(columns=['degree'])
df = df.drop(columns=['date'])

# result_df = df.groupby(['lon', 'lat'], as_index=False).mean()
result_df = df.groupby(['id'], as_index=False).mean()

# 保存结果到新CSV文件
result_df.to_csv(r'e:\work\sv_xiufenganning\地理数据\ade_20k_语义00分割比例数据_04-_.csv', index=False)
