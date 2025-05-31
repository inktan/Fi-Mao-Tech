import pandas as pd

# 读取CSV文件
# df = pd.read_csv(r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\ss_拉萨.csv')  # 替换为你的输入文件名
# df = pd.read_csv(r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\ss_0-_林芝.csv')  # 替换为你的输入文件名
df = pd.read_csv(r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\ss_0-_山南.csv')  # 替换为你的输入文件名

# 分割路径，提取最后两部分
split_result = df['id'].str.split(r'\\', expand=True)  # 注意转义反斜杠

# 获取倒数第二列（folder_name）和最后一列（file_name）
df['folder_name'] = split_result.iloc[:, -2]  # 倒数第二列
df['file_name'] = split_result.iloc[:, -1]    # 最后一列

# 查看结果
print(df[['id', 'folder_name', 'file_name']].head())

# df.to_csv(r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\ss_拉萨_a01.csv', index=False)  # 替换为你想要的输出文件名
# df.to_csv(r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\ss_林芝_a01.csv', index=False)  # 替换为你想要的输出文件名
df.to_csv(r'e:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\街景\ss_山南_a01.csv', index=False)  # 替换为你想要的输出文件名
