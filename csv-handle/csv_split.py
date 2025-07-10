import pandas as pd

# 读取CSV文件
df = pd.read_csv(r'e:\work\sv_xiufenganning\地理数据\ade_20k_语义00分割比例数据_01-_.csv')  # 替换为你的输入文件名

# 分割路径，提取最后两部分
split_result = df['id'].str.split(r'\\', expand=True)  # 注意转义反斜杠

# 获取倒数第二列（folder_name）和最后一列（file_name）
# df['folder_name'] = split_result.iloc[:, -2]  # 倒数第二列
df['id'] = split_result.iloc[:, -1]    # 最后一列
# df.drop(columns=['id'], inplace=True)  # 删除原来的'id'列

# 查看结果
# print(df[['id', 'folder_name', 'file_name']].head())

df.to_csv(r'e:\work\sv_xiufenganning\地理数据\ade_20k_语义00分割比例数据_02-_.csv', index=False)  # 替换为你想要的输出文件名




